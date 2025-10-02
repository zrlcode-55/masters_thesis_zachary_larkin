"""
Base class for Byzantine attack strategies.
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
import numpy as np

from sensors.ground_truth import GroundTruth


class AttackType(Enum):
    """Types of Byzantine attacks."""
    MIMIC = "mimic"           # IoU-passing bias injection (novel threat)
    SPIKE = "spike"           # Large outlier injection (classical)
    DRIFT = "drift"           # Slow bias accumulation (classical)
    COLLIDER = "collider"     # PHY-layer jamming (DoS)
    RANDOM = "random"         # Unstructured noise (baseline)


class ByzantineAttack(ABC):
    """
    Abstract base class for Byzantine adversarial strategies.
    
    Byzantine nodes can lie arbitrarily about sensor readings to
    bias consensus estimates or prevent convergence.
    """
    
    def __init__(
        self,
        node_id: int,
        ground_truth: GroundTruth,
        attack_type: AttackType,
        seed: Optional[int] = None
    ):
        """
        Initialize Byzantine attacker.
        
        Args:
            node_id: Unique node identifier
            ground_truth: Access to true values (Byzantine can observe)
            attack_type: Type of attack being performed
            seed: Random seed for reproducibility
        """
        self.node_id = node_id
        self.ground_truth = ground_truth
        self.attack_type = attack_type
        
        # RNG for attack randomness
        if seed is not None:
            self.rng = np.random.RandomState(seed + node_id + 1000)
        else:
            self.rng = np.random.RandomState()
        
        # Attack statistics
        self.num_attacks = 0
        self.last_value = None
    
    @abstractmethod
    def generate_reading(
        self, 
        time: float,
        honest_neighborhood_estimate: Optional[float] = None,
        honest_neighborhood_ci: Optional[tuple] = None
    ) -> float:
        """
        Generate adversarial sensor reading.
        
        Args:
            time: Current simulation time
            honest_neighborhood_estimate: Estimated value from honest neighbors (if available)
            honest_neighborhood_ci: CI from honest neighbors (lower, upper)
            
        Returns:
            Adversarial reading designed to bias consensus
        """
        pass
    
    def generate_confidence_interval(
        self,
        reading: float,
        honest_ci_width: Optional[float] = None
    ) -> tuple:
        """
        Generate adversarial confidence interval.
        
        Some attacks (especially MIMIC) craft CIs to pass acceptance checks.
        
        Args:
            reading: The adversarial reading
            honest_ci_width: Typical CI width from honest nodes
            
        Returns:
            (lower, upper) confidence interval bounds
        """
        # Default: Use honest-like CI width
        if honest_ci_width is None:
            honest_ci_width = 2.0  # Default ~2σ
        
        half_width = honest_ci_width
        return (reading - half_width, reading + half_width)
    
    def reset(self):
        """Reset attack statistics."""
        self.num_attacks = 0
        self.last_value = None
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(id={self.node_id}, attacks={self.num_attacks})"

