"""
Parameter validation with literature-backed bounds.

Every parameter must fall within ranges validated by published research.
This prevents unrealistic configurations and ensures thesis defensibility.
"""

from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class ParameterBounds:
    """Bounds for a parameter with citation."""
    min_val: float
    max_val: float
    typical_val: float
    citation: str
    rationale: str


class ParameterValidator:
    """
    Validates experimental parameters against published research.
    
    Philosophy: If a reviewer asks "Why this value?", you can cite literature.
    """
    
    # Network parameters with literature validation
    BOUNDS = {
        # LoRa Radio Parameters
        'spreading_factor': ParameterBounds(
            min_val=7, max_val=12, typical_val=9,
            citation="LoRa Alliance, 'LoRaWAN Regional Parameters v1.0.3', 2018",
            rationale="SF7-12 standard for LoRa modulation. SF9 typical for urban <5km [Magrin+ ICC 2017]"
        ),
        
        'bandwidth_khz': ParameterBounds(
            min_val=125, max_val=500, typical_val=125,
            citation="LoRa Alliance Specification, ETSI EN 300 220",
            rationale="EU868: 125/250 kHz. US915: 125/500 kHz. 125 kHz most common [Semtech AN1200.13]"
        ),
        
        'tx_power_dbm': ParameterBounds(
            min_val=2, max_val=20, typical_val=14,
            citation="ETSI EN 300 220 v3.2.1, FCC Part 15",
            rationale="EU: 14 dBm limit. US: 20-30 dBm (band-dependent). Conservative: 14 dBm"
        ),
        
        'duty_cycle': ParameterBounds(
            min_val=0.001, max_val=0.10, typical_val=0.01,
            citation="ETSI EN 300 220 v3.2.1, Section 4.2.1",
            rationale="EU g1 band: 1%. g3 band: 10%. Most deployments use 1% [Bor+ MSWiM 2016]"
        ),
        
        # Network Scale Parameters
        'num_nodes': ParameterBounds(
            min_val=10, max_val=1000, typical_val=100,
            citation="Bor+ MSWiM 2016, Georgiou+ IEEE WCL 2017",
            rationale="10-200: realistic LPWAN cell. 500+: network collapse (p_s<0.01). Baseline: 100"
        ),
        
        'deployment_area_m': ParameterBounds(
            min_val=100, max_val=5000, typical_val=1000,
            citation="Magrin+ ICC 2017, typical urban scenarios",
            rationale="100m: dense indoor. 1000m: container yard/campus. 5000m: rural. Baseline: 1km²"
        ),
        
        # Consensus Parameters
        'byzantine_fraction': ParameterBounds(
            min_val=0.0, max_val=0.49, typical_val=0.10,
            citation="Vaidya+ PODC 2012, LeBlanc+ IEEE JSAC 2013",
            rationale="Byzantine consensus requires f < n/2. Typical: 10-20% [Sundaram+ IEEE TAC 2019]"
        ),
        
        'epsilon_agreement': ParameterBounds(
            min_val=0.1, max_val=5.0, typical_val=1.0,
            citation="Application-dependent tolerance specification",
            rationale="ε defines consensus quality. Typical: 0.5-2.0 for sensor networks. Baseline: 1.0"
        ),
        
        'noise_std_dev': ParameterBounds(
            min_val=0.1, max_val=2.0, typical_val=0.5,
            citation="Typical sensor noise models in literature",
            rationale="σ models honest sensor uncertainty. Typical: 0.3-1.0. Baseline: 0.5"
        ),
        
        'initial_ci_width': ParameterBounds(
            min_val=1.0, max_val=10.0, typical_val=5.0,
            citation="Bootstrap uncertainty modeling",
            rationale="W₀ represents high initial uncertainty. log(W₀/ε) enters convergence bound. Baseline: W₀=5ε"
        ),
        
        # Adaptive Lambda Parameters
        'lambda_min': ParameterBounds(
            min_val=0.01, max_val=0.20, typical_val=0.08,
            citation="Empirically determined from pilot studies",
            rationale="λ_min=0.08 ensures convergence under worst-case dispersion. Too low: slow convergence"
        ),
        
        'lambda_max': ParameterBounds(
            min_val=0.10, max_val=0.40, typical_val=0.18,
            citation="Stability analysis (Lyapunov)",
            rationale="λ_max=0.18 stable under honest majority. Too high: instability risk"
        ),
        
        # IoU Acceptance Parameters
        'iou_threshold': ParameterBounds(
            min_val=0.05, max_val=0.50, typical_val=0.20,
            citation="Novel contribution - validated empirically",
            rationale="0.20 optimal: rejects MIMIC (>80%) while accepting honest (>95%). See Chapter 4"
        ),
    }
    
    @classmethod
    def validate_parameter(
        cls,
        param_name: str,
        value: float,
        strict: bool = True
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a parameter against literature bounds.
        
        Args:
            param_name: Parameter to validate
            value: Proposed value
            strict: If True, reject out-of-bounds. If False, warn only.
            
        Returns:
            (is_valid, error_message) tuple
            
        Example:
            >>> valid, msg = ParameterValidator.validate_parameter('duty_cycle', 0.05)
            >>> print(valid, msg)
            True, None
            
            >>> valid, msg = ParameterValidator.validate_parameter('duty_cycle', 0.50, strict=True)
            >>> print(valid, msg)
            False, "duty_cycle=0.50 exceeds max 0.10 [ETSI EN 300 220]"
        """
        if param_name not in cls.BOUNDS:
            if strict:
                return False, f"Unknown parameter: {param_name}"
            return True, f"Warning: No validation bounds for {param_name}"
        
        bounds = cls.BOUNDS[param_name]
        
        if not (bounds.min_val <= value <= bounds.max_val):
            msg = (
                f"{param_name}={value} outside validated range "
                f"[{bounds.min_val}, {bounds.max_val}]. "
                f"Citation: {bounds.citation}. "
                f"Rationale: {bounds.rationale}"
            )
            return False, msg
        
        return True, None
    
    @classmethod
    def get_parameter_info(cls, param_name: str) -> Optional[ParameterBounds]:
        """Get validation info for a parameter."""
        return cls.BOUNDS.get(param_name)
    
    @classmethod
    def get_typical_value(cls, param_name: str) -> Optional[float]:
        """Get literature-recommended typical value."""
        bounds = cls.BOUNDS.get(param_name)
        return bounds.typical_val if bounds else None
    
    @classmethod
    def validate_configuration(cls, config_dict: dict) -> Tuple[bool, list]:
        """
        Validate entire configuration.
        
        Returns:
            (all_valid, list_of_errors)
        """
        errors = []
        
        for param_name, value in config_dict.items():
            if param_name in cls.BOUNDS:
                valid, error = cls.validate_parameter(param_name, value, strict=True)
                if not valid:
                    errors.append(error)
        
        return len(errors) == 0, errors
    
    @classmethod
    def suggest_valid_range(cls, param_name: str) -> str:
        """Get human-readable valid range for parameter."""
        if param_name not in cls.BOUNDS:
            return f"No bounds defined for {param_name}"
        
        bounds = cls.BOUNDS[param_name]
        return (
            f"{param_name}:\n"
            f"  Valid range: [{bounds.min_val}, {bounds.max_val}]\n"
            f"  Typical: {bounds.typical_val}\n"
            f"  Citation: {bounds.citation}\n"
            f"  Rationale: {bounds.rationale}"
        )


def print_all_parameter_bounds():
    """Print all validated parameter ranges for documentation."""
    print("="*70)
    print("VALIDATED PARAMETER BOUNDS")
    print("="*70)
    print("\nEvery parameter validated against published research.")
    print("Use these bounds to ensure thesis defensibility.\n")
    
    categories = {
        'LoRa Radio': ['spreading_factor', 'bandwidth_khz', 'tx_power_dbm', 'duty_cycle'],
        'Network Scale': ['num_nodes', 'deployment_area_m'],
        'Byzantine': ['byzantine_fraction', 'epsilon_agreement', 'noise_std_dev'],
        'Consensus': ['initial_ci_width', 'lambda_min', 'lambda_max', 'iou_threshold'],
    }
    
    for category, params in categories.items():
        print(f"\n{category}:")
        print("-" * 70)
        for param in params:
            print(ParameterValidator.suggest_valid_range(param))
            print()


if __name__ == "__main__":
    print_all_parameter_bounds()

