"""
SPIKE attack: Classical outlier injection.

Sends extreme values far from truth to test robustness of trimming/filtering.
This is the "dumb" attack that most Byzantine consensus work defends against.
"""

from typing import Optional

from .base_attack import ByzantineAttack, AttackType
from sensors.ground_truth import GroundTruth


class SpikeAttack(ByzantineAttack):
    """
    Classical Byzantine spike attack.
    
    Sends readings far from truth (e.g., truth ± 20°C) to test
    whether trimming and robust estimators can filter outliers.
    
    **Easy to Defend Against**: Trimmed mean, median remove these automatically.
    
    **Purpose in Thesis**: Baseline comparison to show MIMIC is harder.
    """
    
    def __init__(
        self,
        node_id: int,
        ground_truth: GroundTruth,
        spike_magnitude: float = 20.0,
        seed: Optional[int] = None
    ):
        """
        Initialize spike attacker.
        
        Args:
            spike_magnitude: How far from truth to spike (e.g., ±20°C)
        """
        super().__init__(node_id, ground_truth, AttackType.SPIKE, seed)
        self.spike_magnitude = spike_magnitude
    
    def generate_reading(
        self,
        time: float,
        honest_neighborhood_estimate: Optional[float] = None,
        honest_neighborhood_ci: Optional[tuple] = None
    ) -> float:
        """Send extreme outlier."""
        true_value = self.ground_truth.get_value(time)
        
        # Random direction spike
        direction = 1 if self.rng.random() < 0.5 else -1
        reading = true_value + direction * self.spike_magnitude
        
        self.last_value = reading
        self.num_attacks += 1
        
        return reading

