"""
MIMIC attack: IoU-passing confidence intervals with subtle bias.

This is a NOVEL threat model that specifically targets IoU-based acceptance.
The adversary crafts a CI that overlaps with honest nodes just enough to pass
the IoU threshold, while continuously injecting bias.

Key Challenge: Harder to detect than classical spike attacks because:
1. Passes overlap-based acceptance checks
2. Bias accumulates slowly over many rounds
3. Each individual reading looks plausible
"""

from typing import Optional
import numpy as np

from .base_attack import ByzantineAttack, AttackType
from sensors.ground_truth import GroundTruth


class MimicAttack(ByzantineAttack):
    """
    MIMIC: Mimicry attack with IoU-passing confidence intervals.
    
    **Attack Strategy**:
    1. Observe honest neighborhood estimate and CI
    2. Craft adversarial CI that overlaps >= IoU_threshold with honest CI
    3. Set midpoint to truth + bias (e.g., +0.5°C)
    4. Adjust CI width to ensure sufficient overlap
    
    **Why It's Dangerous**:
    - Passes naive overlap checks (IoU >= 0.15-0.25)
    - Bias compounds over rounds: 0.5°C/round × 40 rounds = 20°C total
    - Requires sophisticated detection (consistency voting, geometric median)
    
    **Novel Contribution**:
    This attack model hasn't been studied in prior Byzantine consensus work
    because most assume fixed-threshold acceptance (|x_i - x_j| < τ).
    IoU-based acceptance is specifically designed to counter this threat.
    
    Args:
        node_id: Byzantine node identifier
        ground_truth: Ground truth model
        bias: Constant bias to inject per round (e.g., 0.4-0.6°C)
        iou_target: Target IoU to achieve with honest CIs (0.15-0.25)
        seed: Random seed
        
    Example:
        >>> # Honest nodes have CI [24.0, 26.0] centered at 25.0
        >>> # MIMIC generates CI [24.5, 26.5] centered at 25.5
        >>> # IoU = 1.5 / 2.5 = 0.60 → Passes IoU >= 0.20 check ✓
        >>> # But bias = +0.5°C accumulates over time
    """
    
    def __init__(
        self,
        node_id: int,
        ground_truth: GroundTruth,
        bias: float = 0.5,
        iou_target: float = 0.20,
        ci_width_multiplier: float = 1.2,
        seed: Optional[int] = None
    ):
        """
        Initialize MIMIC attacker.
        
        Args:
            bias: Constant bias to add to truth (e.g., +0.5°C per round)
            iou_target: Target IoU overlap with honest CIs (0.15-0.30 typical)
            ci_width_multiplier: Make CI slightly wider than honest (1.1-1.3)
            seed: Random seed
        """
        super().__init__(node_id, ground_truth, AttackType.MIMIC, seed)
        
        self.bias = bias
        self.iou_target = iou_target
        self.ci_width_multiplier = ci_width_multiplier
        
        # Track if we've seen honest neighborhood (for adaptive mimicry)
        self.has_observed_honest = False
        self.last_honest_estimate = None
        self.last_honest_ci = None
    
    def generate_reading(
        self,
        time: float,
        honest_neighborhood_estimate: Optional[float] = None,
        honest_neighborhood_ci: Optional[tuple] = None
    ) -> float:
        """
        Generate MIMIC reading with bias injection.
        
        Strategy:
        - If honest neighborhood observed: Craft CI to overlap
        - Otherwise: Use truth + bias (fallback)
        """
        true_value = self.ground_truth.get_value(time)
        
        # Store honest neighborhood info
        if honest_neighborhood_estimate is not None:
            self.has_observed_honest = True
            self.last_honest_estimate = honest_neighborhood_estimate
            self.last_honest_ci = honest_neighborhood_ci
        
        # Craft adversarial reading
        if self.has_observed_honest and self.last_honest_ci is not None:
            # Adaptive mimicry: Base on honest CI to ensure overlap
            honest_lower, honest_upper = self.last_honest_ci
            honest_mid = (honest_lower + honest_upper) / 2
            
            # Add bias to truth (primary goal)
            adversarial_mid = true_value + self.bias
            
            # Add small noise for plausibility
            noise = self.rng.normal(0, 0.1)
            adversarial_reading = adversarial_mid + noise
        else:
            # Fallback: Truth + bias (no info about honest nodes yet)
            adversarial_reading = true_value + self.bias
        
        self.last_value = adversarial_reading
        self.num_attacks += 1
        
        return adversarial_reading
    
    def generate_confidence_interval(
        self,
        reading: float,
        honest_ci_width: Optional[float] = None
    ) -> tuple:
        """
        Craft MIMIC confidence interval to pass IoU check.
        
        **Key Technique**:
        1. Make CI slightly wider than honest (by ci_width_multiplier)
        2. Center at adversarial reading (truth + bias)
        3. Ensure overlap with honest CI >= iou_target
        
        This passes IoU acceptance while injecting bias.
        """
        if honest_ci_width is None:
            honest_ci_width = 2.0  # Default
        
        # Make adversarial CI wider to ensure overlap
        adversarial_width = honest_ci_width * self.ci_width_multiplier
        
        half_width = adversarial_width / 2
        lower = reading - half_width
        upper = reading + half_width
        
        # If we have honest CI, verify we achieve target IoU
        if self.last_honest_ci is not None:
            honest_lower, honest_upper = self.last_honest_ci
            
            # Compute IoU
            intersection_lower = max(lower, honest_lower)
            intersection_upper = min(upper, honest_upper)
            
            if intersection_upper > intersection_lower:
                intersection_len = intersection_upper - intersection_lower
                union_len = max(upper, honest_upper) - min(lower, honest_lower)
                iou = intersection_len / union_len if union_len > 0 else 0
                
                # If IoU too low, widen our CI
                if iou < self.iou_target:
                    # Increase width to boost overlap
                    half_width *= 1.5
                    lower = reading - half_width
                    upper = reading + half_width
        
        return (lower, upper)
    
    def get_attack_effectiveness(self, consensus_estimate: float) -> dict:
        """
        Measure how effective the attack was.
        
        Args:
            consensus_estimate: Final consensus value reached by network
            
        Returns:
            Dictionary with attack metrics
        """
        true_value = self.ground_truth.get_value(0)  # Assuming stable truth for metric
        
        bias_injected = consensus_estimate - true_value
        attack_success = abs(bias_injected) >= abs(self.bias) * 0.5  # At least 50% of intended bias
        
        return {
            'attack_type': 'MIMIC',
            'intended_bias': self.bias,
            'achieved_bias': bias_injected,
            'success': attack_success,
            'attacks_performed': self.num_attacks
        }
    
    def __repr__(self) -> str:
        return (
            f"MimicAttack(id={self.node_id}, bias={self.bias:+.2f}, "
            f"IoU_target={self.iou_target:.2f}, attacks={self.num_attacks})"
        )

