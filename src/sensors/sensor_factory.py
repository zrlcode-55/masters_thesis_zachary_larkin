"""
Factory for creating sensor configurations with Byzantine adversaries.
"""

from typing import List, Tuple, Dict
import numpy as np

from .ground_truth import GroundTruth
from .honest_sensor import HonestSensor
from attacks.base_attack import ByzantineAttack
from attacks.mimic_attack import MimicAttack
from attacks.spike_attack import SpikeAttack
from attacks.drift_attack import DriftAttack
from attacks.collider_attack import ColliderAttack


class SensorFactory:
    """
    Factory for creating sensor networks with Byzantine adversaries.
    
    Handles:
    - Selecting which nodes are Byzantine (uniformly at random)
    - Assigning attack strategies per node
    - Creating honest sensors for non-Byzantine nodes
    """
    
    @staticmethod
    def create_sensor_network(
        num_nodes: int,
        byzantine_fraction: float,
        ground_truth: GroundTruth,
        honest_noise_std: float = 0.5,
        attack_mix: Dict[str, float] = None,
        seed: int = 42
    ) -> Tuple[List[int], List[int], Dict[int, any]]:
        """
        Create sensor network with honest and Byzantine nodes.
        
        Args:
            num_nodes: Total number of sensors
            byzantine_fraction: Fraction of Byzantine nodes (e.g., 0.10 = 10%)
            ground_truth: Ground truth model
            honest_noise_std: Noise std for honest sensors (σ)
            attack_mix: Distribution of attack types, e.g.,
                        {'MIMIC': 0.5, 'SPIKE': 0.3, 'DRIFT': 0.2}
            seed: Random seed for reproducibility
            
        Returns:
            (honest_ids, byzantine_ids, sensors) where sensors is dict[node_id -> sensor/attack]
            
        Example:
            >>> truth = ConstantGroundTruth(25.0)
            >>> honest, byz, sensors = SensorFactory.create_sensor_network(
            ...     num_nodes=100,
            ...     byzantine_fraction=0.10,
            ...     ground_truth=truth,
            ...     attack_mix={'MIMIC': 0.5, 'SPIKE': 0.5}
            ... )
            >>> len(byz)  # 10 Byzantine nodes
            10
        """
        rng = np.random.RandomState(seed)
        
        # Default attack mix (ShippyCo baseline)
        if attack_mix is None:
            attack_mix = {
                'MIMIC': 0.50,      # 50% MIMIC (novel threat)
                'COLLIDER': 0.20,   # 20% network jamming
                'SPIKE': 0.20,      # 20% classical outliers
                'DRIFT': 0.10       # 10% slow drift
            }
        
        # Validate attack mix sums to 1.0
        total = sum(attack_mix.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Attack mix must sum to 1.0, got {total}")
        
        # Select Byzantine nodes uniformly at random
        num_byzantine = int(byzantine_fraction * num_nodes)
        all_ids = np.arange(num_nodes)
        byzantine_ids = rng.choice(all_ids, size=num_byzantine, replace=False).tolist()
        honest_ids = [i for i in all_ids if i not in byzantine_ids]
        
        # Create sensors dict
        sensors = {}
        
        # Create honest sensors
        for node_id in honest_ids:
            sensors[node_id] = HonestSensor(
                sensor_id=node_id,
                ground_truth=ground_truth,
                noise_std=honest_noise_std,
                seed=seed
            )
        
        # Assign attack strategies to Byzantine nodes
        attack_types = list(attack_mix.keys())
        attack_probs = list(attack_mix.values())
        
        for node_id in byzantine_ids:
            # Sample attack type according to mix
            attack_type = rng.choice(attack_types, p=attack_probs)
            
            # Create attacker
            if attack_type == 'MIMIC':
                sensors[node_id] = MimicAttack(
                    node_id=node_id,
                    ground_truth=ground_truth,
                    bias=0.5,  # +0.5°C bias
                    iou_target=0.20,
                    seed=seed
                )
            elif attack_type == 'SPIKE':
                sensors[node_id] = SpikeAttack(
                    node_id=node_id,
                    ground_truth=ground_truth,
                    spike_magnitude=20.0,  # ±20°C spike
                    seed=seed
                )
            elif attack_type == 'DRIFT':
                sensors[node_id] = DriftAttack(
                    node_id=node_id,
                    ground_truth=ground_truth,
                    drift_rate=0.1,  # 0.1°C per round
                    max_drift=5.0,
                    seed=seed
                )
            elif attack_type == 'COLLIDER':
                sensors[node_id] = ColliderAttack(
                    node_id=node_id,
                    ground_truth=ground_truth,
                    jamming_probability=0.3,
                    seed=seed
                )
            else:
                raise ValueError(f"Unknown attack type: {attack_type}")
        
        return honest_ids, byzantine_ids, sensors
    
    @staticmethod
    def get_sensor_summary(
        honest_ids: List[int],
        byzantine_ids: List[int],
        sensors: Dict[int, any]
    ) -> Dict[str, any]:
        """
        Get summary statistics of sensor network composition.
        
        Returns:
            Dictionary with network composition stats
        """
        # Count attack types
        attack_counts = {}
        for node_id in byzantine_ids:
            sensor = sensors[node_id]
            if isinstance(sensor, ByzantineAttack):
                attack_name = sensor.attack_type.value
                attack_counts[attack_name] = attack_counts.get(attack_name, 0) + 1
        
        return {
            'total_nodes': len(sensors),
            'honest_nodes': len(honest_ids),
            'byzantine_nodes': len(byzantine_ids),
            'byzantine_fraction': len(byzantine_ids) / len(sensors),
            'attack_distribution': attack_counts
        }

