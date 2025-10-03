# PhD Research Codebase Architecture

**Title**: Byzantine-Resilient Consensus in Stochastic Networks: Information-Theoretic Bounds and Optimal Filtering

**Author**: Zachary Larkin, Vanderbilt University

---

## Research Contributions (Novel)

### 1. **Interval-Based Byzantine Filtering Theory**
- **Problem**: Classical Byzantine consensus uses point estimates. Adversaries can craft confidence intervals that pass consistency checks while injecting bias.
- **Contribution**: Formal analysis of IoU-based filtering with **provable bias bounds**
- **Theorem**: Under \(f < n/2\) Byzantine nodes, IoU threshold \(\tau\), honest CI width \(W_h\), we prove bias \(\leq W_h(1-\tau) + O(\sigma\sqrt{\log n})\)

### 2. **Convergence Analysis under Stochastic Communication**
- **Problem**: Classical consensus assumes reliable channels or bounded delays
- **Contribution**: Tight convergence bounds as function of **graph Laplacian spectral gap** and **packet delivery probability**
- **Theorem**: For time-varying graph \(G(t)\) with time-averaged connectivity \(\bar{\lambda}_2\), convergence time \(T_\varepsilon = O(\frac{1}{\bar{\lambda}_2 p_s} \log(W_0/\varepsilon))\)

### 3. **Adaptive Contraction with Provable Stability**
- **Problem**: Fixed contraction rates are either too slow or unstable under attacks
- **Contribution**: Dispersion-dependent \(\lambda(t)\) with **Lyapunov stability proof**
- **Theorem**: Adaptive \(\lambda \in [\lambda_{min}, \lambda_{max}]\) maintains convergence under \(f < \frac{n}{2}(1 - \frac{\sigma}{\sigma_{attack}})\)

### 4. **Information-Theoretic Lower Bounds**
- **Novel**: First lower bound for consensus under **joint** packet loss + Byzantine faults
- **Contribution**: No algorithm can achieve \(\varepsilon\)-consensus faster than \(\Omega(\frac{f}{n p_s} \log(W_0/\varepsilon))\) rounds

---

## Codebase Structure (140+ files if needed)

```
thesis_code_base/
│
├── theory/                          # Mathematical foundations
│   ├── __init__.py
│   ├── graph_theory/
│   │   ├── laplacian_spectrum.py   # λ₂ analysis, connectivity
│   │   ├── time_varying_graphs.py  # G(t) stochastic models
│   │   └── algebraic_connectivity.py
│   │
│   ├── information_theory/
│   │   ├── lower_bounds.py         # Fundamental limits
│   │   ├── channel_capacity.py     # p_s → information rate
│   │   └── byzantine_entropy.py    # Adversarial information
│   │
│   ├── robust_statistics/
│   │   ├── breakdown_points.py     # Formal breakdown analysis
│   │   ├── influence_functions.py  # Sensitivity to outliers
│   │   └── concentration_bounds.py # Sub-Gaussian, Hoeffding
│   │
│   └── convergence_analysis/
│       ├── lyapunov_functions.py   # Stability proofs
│       ├── contraction_mapping.py  # Fixed-point theorems
│       └── stochastic_approximation.py
│
├── algorithms/                      # Core consensus algorithms
│   ├── __init__.py
│   ├── primitives/
│   │   ├── interval_arithmetic.py  # CI operations
│   │   ├── iou_filtering.py        # IoU acceptance with proofs
│   │   ├── robust_aggregation.py   # Geometric median, MoM, Catoni
│   │   └── adaptive_contraction.py # λ(MAD) mapping
│   │
│   ├── consensus_protocols/
│   │   ├── base_protocol.py        # Abstract consensus interface
│   │   ├── interval_consensus.py   # Our novel algorithm
│   │   ├── vaidya_trimmed.py       # Baseline: Vaidya+ 2012
│   │   ├── leblanc_geometric.py    # Baseline: LeBlanc+ 2013
│   │   └── classical_averaging.py  # Baseline: No Byzantine defense
│   │
│   ├── byzantine_attacks/
│   │   ├── attack_interface.py
│   │   ├── interval_mimicry.py     # Novel: IoU-passing bias
│   │   ├── optimal_adversary.py    # Worst-case within f bound
│   │   ├── classical_outliers.py   # Spike attacks
│   │   └── coordinated_bias.py     # Gradient-descent adversary
│   │
│   └── change_detection/
│       ├── cusum.py                # Change point detection
│       ├── glr.py                  # Generalized likelihood ratio
│       └── bayesian_changepoint.py
│
├── network_models/                  # Stochastic communication models
│   ├── __init__.py
│   ├── abstract/
│   │   ├── stochastic_graph.py     # G(t) with p_ij(t)
│   │   ├── packet_delivery_models.py # Bernoulli, Markov chains
│   │   └── duty_cycle_constraints.py
│   │
│   ├── lpwan_physics/              # Radio-realistic parameters
│   │   ├── lora_modulation.py      # SF, BW, CR → airtime
│   │   ├── aloha_collision.py      # Pure ALOHA p_s formula
│   │   ├── path_loss_models.py     # Log-distance, Hata
│   │   └── regulatory_constraints.py # ETSI duty cycle
│   │
│   └── validation/
│       ├── parameter_ranges.py     # Published measurement bounds
│       └── literature_comparison.py
│
├── optimization/                    # Geometric median, robust centers
│   ├── __init__.py
│   ├── weiszfeld.py                # Geometric median solver
│   ├── gradient_descent_robust.py  # Catoni M-estimator
│   ├── median_of_means.py
│   └── trimmed_estimators.py
│
├── analysis/                        # Experimental analysis tools
│   ├── __init__.py
│   ├── convergence_metrics/
│   │   ├── epsilon_agreement.py
│   │   ├── bias_tracking.py
│   │   ├── stability_windows.py
│   │   └── restabilization_time.py
│   │
│   ├── statistical_tests/
│   │   ├── hypothesis_testing.py   # Wilcoxon, Mann-Whitney
│   │   ├── confidence_intervals.py # Bootstrap, percentile
│   │   └── power_analysis.py
│   │
│   └── visualization/
│       ├── convergence_plots.py
│       ├── phase_portraits.py      # Lyapunov visualization
│       └── spectral_analysis.py
│
├── experiments/                     # Experimental framework
│   ├── __init__.py
│   ├── scenarios/
│   │   ├── scenario_base.py
│   │   ├── scaling_laws.py         # N = 50, 100, 200, 500
│   │   ├── byzantine_fractions.py  # f = 0, 0.1, 0.2, 0.3
│   │   └── network_conditions.py   # p_s sweeps
│   │
│   ├── runners/
│   │   ├── single_run.py
│   │   ├── parameter_sweep.py
│   │   ├── multi_seed_parallel.py
│   │   └── ablation_studies.py
│   │
│   └── reproducibility/
│       ├── deterministic_seeding.py
│       ├── version_tracking.py
│       └── data_archival.py
│
├── proofs/                          # Formal proofs (executable)
│   ├── __init__.py
│   ├── theorem_1_iou_bias_bound.py      # Proof validation
│   ├── theorem_2_convergence_time.py
│   ├── theorem_3_adaptive_stability.py
│   ├── lemma_breakdown_point.py
│   └── corollary_optimal_tau.py
│
├── tests/                           # Rigorous validation
│   ├── unit/
│   │   ├── test_interval_arithmetic.py
│   │   ├── test_iou_computation.py
│   │   ├── test_robust_estimators.py
│   │   └── test_laplacian_spectrum.py
│   │
│   ├── integration/
│   │   ├── test_consensus_protocols.py
│   │   ├── test_byzantine_resilience.py
│   │   └── test_network_models.py
│   │
│   ├── mathematical_properties/     # These SHOULD fail initially!
│   │   ├── test_theorem_1_holds.py  # Bias ≤ proven bound?
│   │   ├── test_theorem_2_holds.py  # Convergence ≤ derived T_ε?
│   │   ├── test_breakdown_points.py # Geometric median ≥ 0.5?
│   │   ├── test_iou_optimal_threshold.py # Best τ by theory?
│   │   └── test_information_lower_bound.py
│   │
│   ├── statistical_validation/
│   │   ├── test_hypothesis_convergence.py
│   │   ├── test_null_no_byzantine.py
│   │   └── test_power_analysis.py
│   │
│   └── regression/
│       ├── test_published_results.py  # Bor+ 2016, Vaidya+ 2012
│       └── test_baseline_algorithms.py
│
├── data/                            # Experimental data
│   ├── raw/                         # Per-run results
│   ├── processed/                   # Aggregated statistics
│   ├── figures/                     # Publication-ready plots
│   └── tables/                      # LaTeX tables
│
├── benchmarks/                      # Performance baselines
│   ├── classical_algorithms/
│   │   ├── vaidya_2012.py
│   │   ├── leblanc_2013.py
│   │   └── sundaram_2019.py
│   │
│   └── performance_profiles/
│
├── docs/
│   ├── ARCHITECTURE.md              # This file
│   ├── MATHEMATICAL_FOUNDATIONS.md  # Core theorems & proofs
│   ├── EXPERIMENTAL_PROTOCOL.md     # Reproducibility guide
│   ├── LITERATURE_REVIEW.md         # Positioning in field
│   └── API_REFERENCE.md
│
├── config/
│   ├── experiments/
│   │   ├── scaling_study.yaml
│   │   ├── byzantine_robustness.yaml
│   │   └── network_conditions.yaml
│   │
│   └── parameters/
│       ├── validated_ranges.yaml    # From published work
│       └── sensitivity_bounds.yaml
│
├── scripts/
│   ├── run_main_experiments.py
│   ├── generate_figures.py
│   ├── compile_latex_tables.py
│   └── verify_all_proofs.py
│
├── notebooks/                       # Analysis notebooks
│   ├── 01_theorem_validation.ipynb
│   ├── 02_convergence_analysis.ipynb
│   ├── 03_optimal_parameters.ipynb
│   └── 04_comparison_baselines.ipynb
│
├── setup.py
├── requirements.txt
├── pytest.ini
├── .gitignore
└── README.md
```

---

## Design Principles

### 1. **Theory-First Development**
- Every algorithm has a corresponding theorem in `/proofs/`
- Tests validate mathematical properties, not just "does it run"
- Proofs are executable code (computational verification)

### 2. **Separation of Concerns**
- **Theory** (`/theory/`): Pure mathematics, domain-agnostic
- **Algorithms** (`/algorithms/`): Implementations with complexity analysis
- **Network Models** (`/network_models/`): Stochastic communication abstractions
- **Experiments** (`/experiments/`): Validation and empirical studies

### 3. **Rigorous Testing Philosophy**
```python
# tests/mathematical_properties/test_theorem_1_holds.py
def test_iou_bias_bound_holds():
    """
    Theorem 1: Under f < n/2 Byzantine nodes with IoU threshold τ,
    honest CI width W_h, sensor noise σ, the consensus bias satisfies:
    
        |x_consensus - x_true| ≤ W_h(1-τ) + O(σ√(log n))
    
    This test MUST initially FAIL because we haven't proven τ = 0.20
    is optimal. Engineering the algorithm to pass this IS the research.
    """
    # Run consensus with proven Byzantine model
    # Measure actual bias
    # Compare to theoretical bound
    # ASSERT: actual_bias ≤ theoretical_bound + tolerance
```

### 4. **No Application Framing**
- ❌ "ShippyCo container yard"
- ✅ "Stochastic network with duty-cycle constraints"
- ❌ "Temperature sensors"
- ✅ "Scalar consensus with bounded noise σ"

---

## Mathematical Workflow

```
1. Formalize Problem → theory/problem_statement.py
2. Derive Bounds → theory/convergence_analysis/
3. Prove Properties → proofs/theorem_*.py
4. Implement Algorithm → algorithms/
5. Create Adversarial Test → tests/mathematical_properties/
6. Validate Empirically → experiments/
7. Compare to Baselines → benchmarks/
```

---

## Novel Contributions Implementation Map

| Contribution | Theory Module | Algorithm Module | Test Module |
|--------------|---------------|------------------|-------------|
| IoU Bias Bound | `theory/robust_statistics/breakdown_points.py` | `algorithms/primitives/iou_filtering.py` | `tests/mathematical_properties/test_theorem_1_holds.py` |
| Convergence under p_s | `theory/convergence_analysis/stochastic_approximation.py` | `algorithms/consensus_protocols/interval_consensus.py` | `tests/mathematical_properties/test_theorem_2_holds.py` |
| Adaptive λ Stability | `theory/convergence_analysis/lyapunov_functions.py` | `algorithms/primitives/adaptive_contraction.py` | `tests/mathematical_properties/test_theorem_3_holds.py` |
| Information Lower Bound | `theory/information_theory/lower_bounds.py` | N/A (theoretical) | `tests/mathematical_properties/test_information_lower_bound.py` |

---

## Example: Theorem → Implementation → Test

**Theorem 1 (IoU Bias Bound)**:

```python
# theory/robust_statistics/iou_bias_theorem.py
def compute_bias_upper_bound(W_h, tau, sigma, n, confidence=0.95):
    """
    Compute theoretical upper bound on consensus bias.
    
    Under assumptions:
    - f < n/2 Byzantine nodes
    - Honest nodes have CI width W_h
    - Sensor noise σ (sub-Gaussian)
    - IoU acceptance threshold τ
    
    Returns:
        Theoretical bias bound B(τ, σ, n)
    """
    adversarial_term = W_h * (1 - tau)
    statistical_term = sigma * np.sqrt(2 * np.log(n / (1 - confidence)))
    return adversarial_term + statistical_term
```

```python
# algorithms/primitives/iou_filtering.py
def iou_accept_filter(ci_local, ci_received, tau):
    """
    IoU-based acceptance filter.
    
    Accepts if IoU(ci_local, ci_received) ≥ τ
    """
    intersection = interval_intersection(ci_local, ci_received)
    union = interval_union(ci_local, ci_received)
    iou = len(intersection) / len(union) if len(union) > 0 else 0.0
    return iou >= tau
```

```python
# tests/mathematical_properties/test_theorem_1_holds.py
@pytest.mark.parametrize("n,f,tau,sigma", [
    (100, 10, 0.20, 0.5),
    (200, 20, 0.25, 0.3),
])
def test_iou_bias_bound_holds(n, f, tau, sigma):
    """
    CRITICAL TEST: This validates our main theoretical contribution.
    
    Expected initial behavior: FAIL (we haven't optimized τ yet)
    Research goal: Find optimal τ that makes this pass
    """
    # Setup
    W_h = 2.0  # Honest CI width
    truth = 25.0
    
    # Compute theoretical bound
    bound = compute_bias_upper_bound(W_h, tau, sigma, n)
    
    # Run consensus algorithm
    result = run_interval_consensus(
        n=n, f=f, tau=tau, sigma=sigma, W_init=W_h, truth=truth
    )
    
    # Measure actual bias
    actual_bias = abs(result.consensus_value - truth)
    
    # THE TEST: Does our algorithm achieve the proven bound?
    assert actual_bias <= bound, \
        f"Bias {actual_bias:.3f} exceeds theoretical bound {bound:.3f}"
```

---

## Next Steps

1. **Create mathematical foundations** (`docs/MATHEMATICAL_FOUNDATIONS.md`)
2. **Implement core theory modules** (`theory/`)
3. **Build rigorous test framework** (`tests/mathematical_properties/`)
4. **Implement algorithms to pass tests** (`algorithms/`)
5. **Validate against baselines** (`benchmarks/`)

This is **PhD-level research**, not engineering. The tests define the mathematical properties we must prove and achieve.


