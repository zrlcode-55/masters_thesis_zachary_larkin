"""
COLLIDER attack: PHY-layer denial-of-service.

Transmits during busy periods to cause packet collisions for honest nodes.
This is a network-layer attack rather than data-layer.
"""

from typing import Optional

from .base_attack import ByzantineAttack, AttackType
from sensors.ground_truth import GroundTruth


class ColliderAttack(ByzantineAttack):
    """
    COLLIDER: Network jamming attack.
    
    **Strategy**: Transmit extra packets during high network load
    to increase collision probability for honest transmissions.
    
    **Effect**: Reduces p_s (packet success) for honest nodes,
    slowing convergence without directly biasing estimates.
    
    **Defense**: Byzantine nodes can't be prevented from transmitting,
    but we track delivery ratios and adjust convergence bounds.
    """
    
    def __init__(
        self,
        node_id: int,
        ground_truth: GroundTruth,
        jamming_probability: float = 0.3,
        seed: Optional[int] = None
    ):
        """
        Initialize collider attacker.
        
        Args:
            jamming_probability: Probability of sending jamming packet per round
        """
        super().__init__(node_id, ground_truth, AttackType.COLLIDER, seed)
        self.jamming_probability = jamming_probability
        self.jamming_packets_sent = 0
    
    def generate_reading(
        self,
        time: float,
        honest_neighborhood_estimate: Optional[float] = None,
        honest_neighborhood_ci: Optional[tuple] = None
    ) -> float:
        """
        Generate reading (may be ignored, attack is at PHY layer).
        
        The actual attack happens by sending extra packets via network.transmit().
        """
        # Send plausible-looking data (attack is in extra transmissions)
        true_value = self.ground_truth.get_value(time)
        reading = true_value + self.rng.normal(0, 0.5)
        
        self.last_value = reading
        self.num_attacks += 1
        
        return reading
    
    def should_jam(self) -> bool:
        """
        Decide whether to send jamming packet this round.
        
        Returns:
            True if should send extra collision-inducing packet
        """
        if self.rng.random() < self.jamming_probability:
            self.jamming_packets_sent += 1
            return True
        return False
    
    def reset(self):
        """Reset jamming statistics."""
        super().reset()
        self.jamming_packets_sent = 0

