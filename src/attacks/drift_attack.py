"""
DRIFT attack: Slow bias accumulation over time.

Harder to detect than spikes but easier than MIMIC.
"""

from typing import Optional

from .base_attack import ByzantineAttack, AttackType
from sensors.ground_truth import GroundTruth


class DriftAttack(ByzantineAttack):
    """
    Slow drift attack: Bias increases gradually over time.
    
    **Strategy**: Start near truth, slowly drift away.
    - Round 1: truth + 0.1°C
    - Round 10: truth + 1.0°C  
    - Round 50: truth + 5.0°C
    
    **Harder than SPIKE**: Not immediately obvious as outlier.
    **Easier than MIMIC**: Doesn't craft CIs to pass acceptance.
    """
    
    def __init__(
        self,
        node_id: int,
        ground_truth: GroundTruth,
        drift_rate: float = 0.1,  # °C per round
        max_drift: float = 5.0,
        seed: Optional[int] = None
    ):
        """
        Initialize drift attacker.
        
        Args:
            drift_rate: Bias increase per attack (e.g., 0.1°C/round)
            max_drift: Maximum total drift
        """
        super().__init__(node_id, ground_truth, AttackType.DRIFT, seed)
        self.drift_rate = drift_rate
        self.max_drift = max_drift
        self.current_drift = 0.0
    
    def generate_reading(
        self,
        time: float,
        honest_neighborhood_estimate: Optional[float] = None,
        honest_neighborhood_ci: Optional[tuple] = None
    ) -> float:
        """Generate drifting reading."""
        true_value = self.ground_truth.get_value(time)
        
        # Increase drift (capped at max)
        self.current_drift = min(
            self.current_drift + self.drift_rate,
            self.max_drift
        )
        
        reading = true_value + self.current_drift
        
        self.last_value = reading
        self.num_attacks += 1
        
        return reading
    
    def reset(self):
        """Reset drift accumulation."""
        super().reset()
        self.current_drift = 0.0

