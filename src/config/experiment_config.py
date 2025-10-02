"""
Experiment configuration with validation.

YAML-driven, validated against published research.
"""

from dataclasses import dataclass, asdict, field
from typing import Dict, List, Optional, Tuple
import yaml

from .parameter_validator import ParameterValidator


@dataclass
class NetworkConfig:
    """
    Network configuration with validation.
    
    All parameters validated against published LoRaWAN research.
    """
    # LoRa radio parameters
    spreading_factor: int = 9
    bandwidth_hz: int = 125_000
    tx_power_dbm: int = 14
    duty_cycle: float = 0.01
    coding_rate: int = 1  # 4/(4+CR) = 4/5
    
    # Network scale
    num_nodes: int = 100
    deployment_area_m: int = 1000
    
    # Payload configuration
    payload_bytes: int = 51  # LoRaWAN MAC (13) + App (38)
    
    def __post_init__(self):
        """Validate all parameters."""
        self._validate()
    
    def _validate(self):
        """Validate configuration against literature bounds."""
        validation_map = {
            'spreading_factor': self.spreading_factor,
            'bandwidth_khz': self.bandwidth_hz / 1000,
            'tx_power_dbm': self.tx_power_dbm,
            'duty_cycle': self.duty_cycle,
            'num_nodes': self.num_nodes,
            'deployment_area_m': self.deployment_area_m,
        }
        
        errors = []
        for param, value in validation_map.items():
            valid, error = ParameterValidator.validate_parameter(param, value)
            if not valid:
                errors.append(error)
        
        if errors:
            raise ValueError(
                f"Network configuration validation failed:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )


@dataclass
class ConsensusConfig:
    """
    Consensus algorithm configuration with validation.
    """
    # Agreement parameters
    epsilon: float = 1.0  # ε-agreement tolerance
    initial_ci_width: float = 5.0  # W0
    
    # Sensor noise
    noise_std_dev: float = 0.5  # σ for honest sensors
    
    # Adaptive contraction
    lambda_min: float = 0.08
    lambda_max: float = 0.18
    
    # IoU acceptance (NOVEL CONTRIBUTION)
    iou_threshold: float = 0.20
    consistency_vote_threshold: float = 0.50  # Require 50% support
    
    # Trimming parameters
    trim_min: int = 2  # Min trim per side
    trim_max_fraction: float = 0.20  # Max 20% of values
    
    # Robust estimator choice
    estimator: str = "geometric_median"  # Options: trimmed_mean, geometric_median, mom, catoni
    
    # Change detection
    change_detection: str = "cusum"  # Options: cusum, glr, off
    
    def __post_init__(self):
        """Validate all parameters."""
        self._validate()
    
    def _validate(self):
        """Validate configuration."""
        validation_map = {
            'epsilon_agreement': self.epsilon,
            'initial_ci_width': self.initial_ci_width,
            'noise_std_dev': self.noise_std_dev,
            'lambda_min': self.lambda_min,
            'lambda_max': self.lambda_max,
            'iou_threshold': self.iou_threshold,
        }
        
        errors = []
        for param, value in validation_map.items():
            valid, error = ParameterValidator.validate_parameter(param, value)
            if not valid:
                errors.append(error)
        
        # Validate λ_min < λ_max
        if self.lambda_min >= self.lambda_max:
            errors.append(f"lambda_min ({self.lambda_min}) must be < lambda_max ({self.lambda_max})")
        
        # Validate estimator choice
        valid_estimators = ['trimmed_mean', 'geometric_median', 'mom', 'catoni']
        if self.estimator not in valid_estimators:
            errors.append(f"estimator must be one of {valid_estimators}, got '{self.estimator}'")
        
        if errors:
            raise ValueError(
                f"Consensus configuration validation failed:\n" +
                "\n".join(f"  - {e}" for e in errors)
            )


@dataclass
class AdversarialConfig:
    """Byzantine adversary configuration."""
    byzantine_fraction: float = 0.10
    
    attack_mix: Dict[str, float] = field(default_factory=lambda: {
        'MIMIC': 0.50,
        'COLLIDER': 0.20,
        'SPIKE': 0.20,
        'DRIFT': 0.10
    })
    
    # Attack parameters
    mimic_bias: float = 0.5  # °C per round
    spike_magnitude: float = 20.0  # ±°C
    drift_rate: float = 0.1  # °C per round
    
    def __post_init__(self):
        """Validate configuration."""
        # Validate Byzantine fraction
        valid, error = ParameterValidator.validate_parameter(
            'byzantine_fraction', self.byzantine_fraction
        )
        if not valid:
            raise ValueError(error)
        
        # Validate attack mix sums to 1.0
        total = sum(self.attack_mix.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"attack_mix must sum to 1.0, got {total}")


@dataclass
class GroundTruthConfig:
    """Ground truth dynamics configuration."""
    baseline_value: float = 25.0  # °C
    
    changes: List[Dict] = field(default_factory=lambda: [
        {'time': 0, 'value': 25.0},
        {'time': 1200, 'value': 28.0},  # Door opens at 1200s
        {'time': 1800, 'value': 25.0},  # Door closes at 1800s
    ])


@dataclass
class ExperimentConfig:
    """
    Complete experiment configuration.
    
    Load from YAML, validate against research, run experiments.
    """
    name: str
    description: str
    
    network: NetworkConfig
    consensus: ConsensusConfig
    adversarial: AdversarialConfig
    ground_truth: GroundTruthConfig
    
    # Experimental control
    seeds: List[int] = field(default_factory=lambda: list(range(20)))
    max_rounds: int = 5000
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> 'ExperimentConfig':
        """
        Load configuration from YAML file with validation.
        
        Example YAML:
            name: "ShippyCo Baseline"
            description: "100 nodes, 10% Byzantine, SF9"
            
            network:
              spreading_factor: 9
              num_nodes: 100
              duty_cycle: 0.01
            
            consensus:
              epsilon: 1.0
              lambda_min: 0.08
              lambda_max: 0.18
              iou_threshold: 0.20
        """
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Parse nested configs
        network = NetworkConfig(**data.get('network', {}))
        consensus = ConsensusConfig(**data.get('consensus', {}))
        adversarial = AdversarialConfig(**data.get('adversarial', {}))
        ground_truth = GroundTruthConfig(**data.get('ground_truth', {}))
        
        return cls(
            name=data['name'],
            description=data['description'],
            network=network,
            consensus=consensus,
            adversarial=adversarial,
            ground_truth=ground_truth,
            seeds=data.get('seeds', list(range(20))),
            max_rounds=data.get('max_rounds', 5000)
        )
    
    def to_yaml(self, yaml_path: str):
        """Save configuration to YAML."""
        data = {
            'name': self.name,
            'description': self.description,
            'network': asdict(self.network),
            'consensus': asdict(self.consensus),
            'adversarial': asdict(self.adversarial),
            'ground_truth': asdict(self.ground_truth),
            'seeds': self.seeds,
            'max_rounds': self.max_rounds
        }
        
        with open(yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def validate(self) -> Tuple[bool, List[str]]:
        """
        Comprehensive validation of entire configuration.
        
        Returns:
            (is_valid, list_of_errors)
        """
        errors = []
        
        # Each sub-config validates itself in __post_init__
        # This is a sanity check for cross-config constraints
        
        # Check: num_nodes vs Byzantine fraction
        num_byzantine = int(self.network.num_nodes * self.adversarial.byzantine_fraction)
        if num_byzantine < 1:
            errors.append(
                f"Byzantine fraction {self.adversarial.byzantine_fraction} "
                f"with {self.network.num_nodes} nodes gives {num_byzantine} Byzantine nodes. "
                "Need at least 1 for meaningful experiments."
            )
        
        # Check: epsilon vs noise
        if self.consensus.epsilon < self.consensus.noise_std_dev:
            errors.append(
                f"Warning: epsilon ({self.consensus.epsilon}) < noise_std "
                f"({self.consensus.noise_std_dev}). May not achieve ε-agreement even without attacks."
            )
        
        return len(errors) == 0, errors
    
    def __repr__(self) -> str:
        return (
            f"ExperimentConfig('{self.name}')\n"
            f"  Network: N={self.network.num_nodes}, SF={self.network.spreading_factor}, "
            f"D={self.network.duty_cycle*100:.1f}%\n"
            f"  Consensus: ε={self.consensus.epsilon}, λ∈[{self.consensus.lambda_min}, {self.consensus.lambda_max}], "
            f"IoU={self.consensus.iou_threshold}\n"
            f"  Byzantine: {self.adversarial.byzantine_fraction*100:.0f}% ({int(self.network.num_nodes * self.adversarial.byzantine_fraction)} nodes)\n"
            f"  Seeds: {len(self.seeds)}"
        )

