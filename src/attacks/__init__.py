"""
Byzantine attack strategies for consensus testing.

Implements various adversarial behaviors to test Byzantine resilience:
- MIMIC: IoU-passing attacks with subtle bias
- COLLIDER: PHY-layer jamming during high load
- SPIKE: Classical outlier injection
- DRIFT: Slow bias accumulation
"""

from .base_attack import ByzantineAttack, AttackType
from .mimic_attack import MimicAttack
from .spike_attack import SpikeAttack
from .drift_attack import DriftAttack
from .collider_attack import ColliderAttack

__all__ = [
    'ByzantineAttack',
    'AttackType',
    'MimicAttack',
    'SpikeAttack',
    'DriftAttack',
    'ColliderAttack'
]

