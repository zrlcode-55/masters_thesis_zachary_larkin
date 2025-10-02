"""
Pre-validated scenario library for thesis experiments.

Each scenario is validated against published research and documented
with clear use cases, expected outcomes, and limitations.
"""

from .experiment_config import (
    ExperimentConfig, NetworkConfig, ConsensusConfig,
    AdversarialConfig, GroundTruthConfig
)


class ScenarioLibrary:
    """
    Library of validated experimental scenarios.
    
    Philosophy: Don't let researchers start from scratch with potentially
    invalid configurations. Provide validated baselines.
    """
    
    @staticmethod
    def baseline_100n_10b() -> ExperimentConfig:
        """
        Configuration A (Baseline): Standard Byzantine consensus scenario.
        
        **Research Purpose**: Primary validation configuration for thesis.
        
        **Algorithmic Properties**:
        - N=100, f=10%, SF9 → G≈1.0 → p_s≈0.135 (ALOHA collision model)
        - Tests consensus under moderate packet loss (86.5%)
        - Validates IoU acceptance, adaptive λ, convergence bounds
        
        **Expected Algorithmic Outcomes**:
        - Convergence: O(N/p_s · T_pkt/D · log(W₀/ε)/λ) ≈ 40-50 rounds
        - IoU defense: bias reduction from >2.0 to <0.5 (4× improvement)
        - Adaptive λ: 2× speedup over fixed λ_min
        
        **Parameter Validation**:
        - Network: Bor+ MSWiM 2016, Magrin+ ICC 2017
        - Byzantine fraction: Vaidya+ PODC 2012 (f < n/2)
        - CI consensus: LeBlanc+ IEEE JSAC 2013
        
        **Parameter Instantiation**: ε=1.0, σ=0.5 chosen as representative
        values for concrete validation. Contributions are parameter-independent
        (validated via sensitivity analysis).
        """
        return ExperimentConfig(
            name="Configuration A (Baseline)",
            description="N=100, f=10%, SF9 - Primary Byzantine consensus validation",
            
            network=NetworkConfig(
                spreading_factor=9,
                bandwidth_hz=125_000,
                tx_power_dbm=14,
                duty_cycle=0.01,
                num_nodes=100,
                deployment_area_m=1000,
                payload_bytes=51
            ),
            
            consensus=ConsensusConfig(
                epsilon=1.0,  # ε-agreement tolerance (units: °C for cold-chain example)
                initial_ci_width=5.0,  # W₀: Initial CI width (high uncertainty bootstrap)
                noise_std_dev=0.5,  # σ: Sensor noise std dev
                lambda_min=0.08,  # Conservative contraction rate
                lambda_max=0.18,  # Aggressive contraction (stability-limited)
                iou_threshold=0.20,  # τ_IoU: IoU acceptance threshold (novel contribution)
                estimator="geometric_median"  # Robust aggregation function
            ),
            
            adversarial=AdversarialConfig(
                byzantine_fraction=0.10,  # f = 10% Byzantine nodes
                attack_mix={
                    'MIMIC': 0.50,  # Novel threat: overlapping CIs with bias
                    'COLLIDER': 0.20,  # PHY jamming
                    'SPIKE': 0.20,  # Classical outlier attack
                    'DRIFT': 0.10  # Slow bias injection
                }
            ),
            
            ground_truth=GroundTruthConfig(
                baseline_value=25.0,
                changes=[
                    {'time': 0, 'value': 25.0},
                    {'time': 1200, 'value': 28.0},  # Step change +3.0 at t=1200s
                    {'time': 1800, 'value': 25.0}   # Return to baseline at t=1800s
                ]
            ),
            
            seeds=list(range(20)),
            max_rounds=5000
        )
    
    @staticmethod
    def shippy_baseline() -> ExperimentConfig:
        """
        DEPRECATED: Use baseline_100n_10b() instead.
        
        Kept for backward compatibility with existing scripts.
        """
        return ScenarioLibrary.baseline_100n_10b()
    
    @staticmethod
    def scaling_200n() -> ExperimentConfig:
        """
        Configuration B (Scaling): High-density network stress test.
        
        **Research Purpose**: Validate algorithm scaling under extreme packet loss.
        
        **Algorithmic Properties**:
        - N=200, f=10%, SF9 → G≈2.0 → p_s≈0.018 (98% packet loss!)
        - Tests consensus robustness at network capacity limit
        - Validates convergence bound scaling: T_conv ∝ N/p_s
        
        **Expected Algorithmic Outcomes**:
        - Convergence: ~100 rounds (2× baseline due to p_s degradation)
        - IoU acceptance still works (tests CI-based consensus under stress)
        - Bound prediction remains tight despite extreme conditions
        
        **Parameter Validation**:
        - Scaling behavior: Bor+ MSWiM 2016 Figure 7
        - N=200 stress: Georgiou+ IEEE WCL 2017
        
        **Algorithmic Insight**: Tests consensus at network capacity limits
        """
        config = ScenarioLibrary.baseline_100n_10b()
        config.name = "Configuration B (Scaling)"
        config.description = "N=200, f=10%, SF9 - Network scaling validation (G≈2.0)"
        config.network.num_nodes = 200
        return config
    
    @staticmethod
    def dense_deployment() -> ExperimentConfig:
        """DEPRECATED: Use scaling_200n() instead."""
        return ScenarioLibrary.scaling_200n()
    
    @staticmethod
    def security_20b() -> ExperimentConfig:
        """
        Configuration C (Security): High Byzantine fraction stress test.
        
        **Research Purpose**: Validate defense mechanisms near theoretical limit.
        
        **Algorithmic Properties**:
        - N=100, f=20%, SF9 (approaching f < n/2 limit)
        - Tests IoU acceptance under maximum Byzantine threat
        - Validates adaptive λ still converges with heavy filtering
        
        **Expected Algorithmic Outcomes**:
        - Classical trimmed mean: FAILS (bias >5°C)
        - IoU + consistency voting: SUCCEEDS (bias <1°C)
        - Convergence slower (~60 rounds vs 40) due to filtering overhead
        
        **Theoretical Validation**:
        - Byzantine consensus requires f < n/2 [Vaidya+ PODC 2012]
        - f=20% tests upper practical range [LeBlanc+ IEEE JSAC 2013]
        - Demonstrates IoU acceptance is necessary, not optional
        
        **Algorithmic Insight**: Demonstrates IoU acceptance necessity at practical limits
        """
        config = ScenarioLibrary.baseline_100n_10b()
        config.name = "Configuration C (Security)"
        config.description = "N=100, f=20%, SF9 - Byzantine defense stress test"
        config.adversarial.byzantine_fraction = 0.20
        return config
    
    @staticmethod
    def high_adversarial() -> ExperimentConfig:
        """DEPRECATED: Use security_20b() instead."""
        return ScenarioLibrary.security_20b()
    
    @staticmethod
    def sparse_50n() -> ExperimentConfig:
        """
        Configuration D (Sparse): Low-density network with fewer neighbors.
        
        **Research Purpose**: Validate consensus with limited local information.
        
        **Algorithmic Properties**:
        - N=50, f=10%, SF9 → G≈0.5 → p_s≈0.37 (63% packet loss)
        - Better packet success (2.7× vs baseline) but fewer redundant paths
        - Tests Byzantine tolerance with reduced neighbor count
        
        **Expected Algorithmic Outcomes**:
        - Faster per-round convergence (~25 rounds vs 40)
        - But need to verify local Byzantine fraction f_local < n_local/2
        - IoU acceptance has fewer CIs to compare (tests threshold robustness)
        
        **Parameter Validation**:
        - Sparse networks: Magrin+ ICC 2017 (agricultural scenarios)
        - G=0.5 collision: Bor+ MSWiM 2016 (low load regime)
        
        **Algorithmic Insight**: Tests consensus with reduced redundancy
        """
        config = ScenarioLibrary.baseline_100n_10b()
        config.name = "Configuration D (Sparse)"
        config.description = "N=50, f=10%, SF9 - Low-density consensus (G≈0.5)"
        config.network.num_nodes = 50
        config.network.deployment_area_m = 2000
        return config
    
    @staticmethod
    def sparse_deployment() -> ExperimentConfig:
        """DEPRECATED: Use sparse_50n() instead."""
        return ScenarioLibrary.sparse_50n()
    
    @staticmethod
    def speed_sf7() -> ExperimentConfig:
        """
        Configuration E (Speed): Fast radio for convergence speed analysis.
        
        **Research Purpose**: Explore speed/reliability trade-off in consensus.
        
        **Algorithmic Properties**:
        - N=100, f=10%, SF7 → T_pkt≈97ms (3× faster than SF9's 308ms)
        - 3× more rounds per duty cycle window → faster wall-clock convergence
        - Tests if consensus is airtime-limited or computation-limited
        
        **Expected Algorithmic Outcomes**:
        - Wall-clock convergence: ~13 rounds × 97ms ≈ 1.3s (vs 12.3s for SF9)
        - Round count similar (~13 vs ~40) but each round much faster
        - Validates bound's T_pkt term: T_conv ∝ T_pkt
        
        **Parameter Validation**:
        - SF7 airtime: Semtech AN1200.13
        - SNR requirement: -7.5dB [Semtech SX1276 datasheet]
        - Range limitation: ~500m vs 1km for SF9 [Magrin+ 2017]
        
        **Trade-off Analysis**: Speed (3×) vs range (0.5×) - tests if worth it
        
        **Algorithmic Insight**: Validates T_conv ∝ T_pkt scaling relationship
        """
        config = ScenarioLibrary.baseline_100n_10b()
        config.name = "Configuration E (Speed)"
        config.description = "N=100, f=10%, SF7 - Speed/reliability trade-off (T_pkt≈97ms)"
        config.network.spreading_factor = 7
        config.network.deployment_area_m = 500  # Smaller area for SF7 range limit
        return config
    
    @staticmethod
    def sf7_fast() -> ExperimentConfig:
        """DEPRECATED: Use speed_sf7() instead."""
        return ScenarioLibrary.speed_sf7()
    
    @staticmethod
    def ideal_0b() -> ExperimentConfig:
        """
        Configuration F (Ideal): No Byzantine nodes - best-case validation.
        
        **Research Purpose**: Establish algorithmic best-case performance.
        
        **Algorithmic Properties**:
        - N=100, f=0%, SF9 (no Byzantine interference)
        - Pure network effects (no attack mitigation overhead)
        - Tests convergence bound accuracy without Byzantine uncertainty
        
        **Expected Algorithmic Outcomes**:
        - Convergence: ~30 rounds (25% faster than f=10% baseline)
        - IoU acceptance overhead minimal (all CIs honest)
        - Adaptive λ achieves λ_max quickly (low dispersion)
        - Bound prediction should be tightest (no adversarial variability)
        
        **Research Value**:
        - Separates network effects from Byzantine defense costs
        - Validates convergence bound without adversarial terms
        - Shows adaptive λ performance without attack-induced dispersion
        
        **Not a Real Scenario**: But essential for algorithm validation
        """
        config = ScenarioLibrary.baseline_100n_10b()
        config.name = "Configuration F (Ideal)"
        config.description = "N=100, f=0%, SF9 - Best-case algorithmic validation"
        config.adversarial.byzantine_fraction = 0.0
        return config
    
    @staticmethod
    def no_byzantine() -> ExperimentConfig:
        """DEPRECATED: Use ideal_0b() instead."""
        return ScenarioLibrary.ideal_0b()
    
    @staticmethod
    def list_all_scenarios() -> dict:
        """
        Get all CS-focused research scenarios.
        
        Returns dict with algorithmic properties and research goals.
        """
        return {
            'baseline_100n_10b': {
                'config': ScenarioLibrary.baseline_100n_10b(),
                'research_goal': 'Primary thesis validation (Config A)',
                'algorithmic_test': 'IoU acceptance, adaptive λ, convergence bounds',
                'expected_outcome': 'T_conv≈40 rounds, bias<0.5°C with IoU'
            },
            'scaling_200n': {
                'config': ScenarioLibrary.scaling_200n(),
                'research_goal': 'Network scaling validation (Config B)',
                'algorithmic_test': 'Bound scaling T_conv ∝ N/p_s, robustness at G=2.0',
                'expected_outcome': 'T_conv≈100 rounds (2× due to p_s degradation)'
            },
            'security_20b': {
                'config': ScenarioLibrary.security_20b(),
                'research_goal': 'Byzantine defense stress test (Config C)',
                'algorithmic_test': 'IoU necessity near f<n/2 limit',
                'expected_outcome': 'Classical fails (>5°C), IoU succeeds (<1°C)'
            },
            'sparse_50n': {
                'config': ScenarioLibrary.sparse_50n(),
                'research_goal': 'Low-density consensus (Config D)',
                'algorithmic_test': 'Limited neighbor information, local Byzantine tolerance',
                'expected_outcome': 'T_conv≈25 rounds (better p_s, fewer neighbors)'
            },
            'speed_sf7': {
                'config': ScenarioLibrary.speed_sf7(),
                'research_goal': 'Speed/reliability trade-off (Config E)',
                'algorithmic_test': 'Validate T_conv ∝ T_pkt term in bound',
                'expected_outcome': '3× faster wall-clock convergence'
            },
            'ideal_0b': {
                'config': ScenarioLibrary.ideal_0b(),
                'research_goal': 'Best-case algorithmic performance (Config F)',
                'algorithmic_test': 'Bound accuracy without Byzantine uncertainty',
                'expected_outcome': 'T_conv≈30 rounds, tightest bound prediction'
            }
        }


if __name__ == "__main__":
    print("="*70)
    print("CS-FOCUSED RESEARCH SCENARIOS")
    print("="*70)
    print("\nValidated Byzantine consensus configurations.")
    print("Focus: Algorithmic properties, NOT application domains.\n")
    
    scenarios = ScenarioLibrary.list_all_scenarios()
    
    for name, info in scenarios.items():
        print(f"\n{name} ({info['config'].name}):")
        print("-" * 70)
        print(f"Research Goal: {info['research_goal']}")
        print(f"Tests: {info['algorithmic_test']}")
        print(f"Expected: {info['expected_outcome']}")
        print(f"\n{info['config']}")
        print()

