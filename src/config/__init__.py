"""
Configuration management system.

PhD-level rigor: Every parameter validated against published research.
No magic numbers - everything configurable with cited bounds.
"""

from .experiment_config import ExperimentConfig, NetworkConfig, ConsensusConfig
from .scenario_library import ScenarioLibrary
from .parameter_validator import ParameterValidator

__all__ = [
    'ExperimentConfig',
    'NetworkConfig', 
    'ConsensusConfig',
    'ScenarioLibrary',
    'ParameterValidator'
]

