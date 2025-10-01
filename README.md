# Byzantine-Resilient Consensus for LPWAN Networks: <br/> Continuous Stability Under Radio-Realistic Constraints

**Master's Thesis Implementation**  
Zachary Larkin  
Vanderbilt University, Department of Computer Science

---

## Abstract

Existing Byzantine consensus algorithms assume idealized network models with perfect broadcast or bounded message delays, making them unsuitable for Low-Power Wide-Area Networks (LPWANs) where duty-cycle restrictions, collision-prone uncoordinated MAC protocols, and asymmetric link conditions dominate. Furthermore, prior work focuses on *one-shot convergence* rather than *continuous operation* where ground truth evolves and network topology changes dynamically.

This work presents a novel Byzantine-resilient consensus framework tailored for **LoRaWAN-class networks** that:
1. Operates under **packet loss rates of 40-70%** due to ALOHA collisions and duty-cycle constraints
2. Achieves ε-agreement despite **mimicry attacks** where adversaries craft confidence intervals that pass overlap checks while continuously biasing estimates
3. Tracks **continuous stability** with rigorous re-stabilization timing after environmental changes (e.g., cold-chain door openings)
4. Provides **ns-3-grounded convergence bounds** that predict time-to-consensus using measured packet success probability (p_s), airtime (T_pkt), and adaptive contraction factors (λ)

**Research Gap Addressed**: No prior work combines Byzantine resilience with the extreme radio constraints of LPWAN (1% duty cycle, SF7-12 spreading factors, Class A receive windows) while maintaining continuous operational guarantees.

---

## Novel Contributions

### 1. Scale-Invariant IoU-based Acceptance with Consistency Voting
Traditional Byzantine consensus uses fixed-threshold acceptance (e.g., "reject if |x_i - x_j| > τ"), which fails under mimicry attacks where adversaries fine-tune estimates to pass naive checks.

**Our Approach**: Intersection-over-Union (IoU) on confidence intervals:
```
IoU(CI_i, CI_j) = |CI_i ∩ CI_j| / |CI_i ∪ CI_j|
```
Combined with a **mode-consistency vote** (density-based clustering of estimates), this rejects:
- Adversarial CIs that barely overlap but cluster away from honest majority
- Mimicry attacks that pass pairwise IoU but fail collective density checks

**Theoretical Property**: Under honest majority and bounded sensor noise σ, mimicry bias is bounded by O(σ√(log n)) per round (proof sketch in `docs/theory.md`).

### 2. Continuous Stability Windows & Re-Stabilization Metrics
Unlike prior work measuring T_conv (time to first ε-agreement), we track:
- **Stability duration**: Total time within ε-ball around ground truth
- **Re-stabilization time**: Latency to re-converge after detected changes (CUSUM/GLR)
- **Per-component stability**: Independent tracking in partitioned networks

**Application**: Cold-chain monitoring requires *continuous* trust, not one-shot convergence. Operators need guarantees like "95% of time within ±1°C despite 10% Byzantine nodes."

### 3. Radio-Realistic Convergence Bounds
Classical bounds (e.g., Tsitsiklis, Vaidya) assume synchronous rounds or bounded delays. We derive:

**Theorem (Informal)**: Under p_s packet success probability, λ-contraction per round, and T_pkt/D effective round time (airtime/duty-cycle):
```
T_ε ≤ [log(W_0/ε) / (p_s · log(1/(1-λ)))] · (T_pkt / D)
```
where W_0 is initial CI width, ε is target agreement tolerance, and p_s, λ are measured from ns-3 traces.

**Key Insight**: Duty cycle D and collision-driven p_s directly enter the bound—unlike toy models assuming instant broadcast.

### 4. Adaptive Dispersion-to-Contraction Mapping
Fixed contraction rates (λ = constant) converge slowly under low dispersion and risk instability under high dispersion.

**Our Mechanism**: 
```
λ(round) = f(MAD(accepted_values)) ∈ [λ_min, λ_max]
```
where MAD is median absolute deviation. Under weak neighborhood support (sparse accepted messages), λ is throttled to λ_min/2 for safety.

**Effect**: 2-3× faster convergence in nominal conditions while maintaining robustness during attacks (validated in Section 6).

---

## Architecture & Implementation

### System Architecture
```
┌─────────────────────────────────────────────────────────────┐
│  Experiment Runner (Multi-seed, configuration management)  │
└────────────────────┬────────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────┐          ┌─────▼──────┐
    │ ns-3 PHY │          │ Consensus  │
    │   Layer  │◄────────►│   Engine   │
    └────┬─────┘          └─────┬──────┘
         │                      │
    LoRa Radio            ┌─────┴────────┐
    Collisions            │ - IoU Accept │
    Duty Cycle            │ - Robust Est │
    Class A               │ - Adaptive λ │
                          │ - Tracking   │
                          └──────────────┘
```

### Project Structure
```
.
├── src/
│   ├── network/
│   │   ├── ns3_wrapper.py           # ns-3 Python bindings interface
│   │   ├── lora_config.py           # SF/BW/CR/TxPower configuration
│   │   ├── topology.py              # Node placement (grid-with-jitter)
│   │   └── duty_cycle.py            # Regulatory airtime enforcement
│   │
│   ├── consensus/
│   │   ├── node_state.py            # Per-node CI, quarantine, metadata
│   │   ├── acceptance.py            # IoU + consistency voting
│   │   ├── aggregation.py           # Trimming + robust aggregation
│   │   ├── contraction.py           # Adaptive λ mapping
│   │   └── partition_detector.py    # Component tracking via RX liveness
│   │
│   ├── attacks/
│   │   ├── base_attack.py           # Abstract adversary interface
│   │   ├── mimic_attack.py          # IoU-passing CI with bias injection
│   │   ├── collider_attack.py       # PHY-layer jamming during high load
│   │   ├── spike_attack.py          # Classical outlier injection
│   │   └── drift_attack.py          # Slow bias accumulation
│   │
│   ├── estimators/
│   │   ├── trimmed_mean.py          # α-trimmed mean (fast baseline)
│   │   ├── geometric_median.py      # Weiszfeld's algorithm (breakdown ~0.5)
│   │   ├── median_of_means.py       # MoM with configurable groups
│   │   └── catoni_estimator.py      # Heavy-tailed robust mean
│   │
│   ├── sensors/
│   │   ├── ground_truth.py          # Piecewise truth x*(t) with changes
│   │   ├── honest_sensor.py         # x*(t) + N(0, σ²)
│   │   └── sensor_factory.py        # Instantiate honest/Byzantine sensors
│   │
│   ├── change_detection/
│   │   ├── cusum.py                 # Cumulative sum change detection
│   │   ├── glr.py                   # Generalized likelihood ratio
│   │   └── detector_interface.py    # Abstract detector API
│   │
│   ├── metrics/
│   │   ├── round_metrics.py         # p_s, T_pkt, λ_obs, m_hon per round
│   │   ├── stability_tracker.py     # Enter/exit ε-windows, re-stab time
│   │   ├── convergence_bound.py     # Theoretical T_ε prediction
│   │   └── continuous_metrics.py    # Uptime-in-ε, partition history
│   │
│   └── experiments/
│       ├── config_loader.py         # YAML → dataclass configuration
│       ├── run_experiment.py        # Single-seed experiment
│       ├── run_multi_seed.py        # Parallel multi-seed with aggregation
│       └── scenario_builder.py      # ShippyCo baseline + variants
│
├── config/
│   ├── shippy_baseline.yaml         # N=100, β=0.10, SF=9 baseline
│   ├── dense_deployment.yaml        # N=200, smaller area (higher collision)
│   ├── sparse_deployment.yaml       # N=50, larger area (lower p_s)
│   └── high_adversarial.yaml        # β=0.20, mixed attack strategies
│
├── results/                         # Timestamped experiment outputs
├── notebooks/
│   ├── convergence_analysis.ipynb   # T_meas vs T_pred, gap ratios
│   ├── stability_windows.ipynb      # Continuous uptime analysis
│   ├── attack_effectiveness.ipynb   # MIMIC vs SPIKE vs COLLIDER
│   └── parameter_sensitivity.ipynb  # IoU_tau, λ_min/max, trim levels
│
├── tests/
│   ├── test_iou_acceptance.py
│   ├── test_estimators.py
│   ├── test_mimic_attack.py
│   └── test_convergence_bound.py
│
├── docs/
│   ├── theory.md                    # Proof sketches, bound derivations
│   ├── ns3_integration.md           # ns-3 setup guide, PHY trace details
│   └── experiment_protocol.md       # Reproducibility checklist
│
├── requirements.txt
├── README.md
└── LICENSE
```

## Installation

### Prerequisites
- Python 3.9+
- ns-3 (version 3.36+) with Python bindings
- C++ compiler (for ns-3)

### Setup
```bash
# Install Python dependencies
pip install -r requirements.txt

# Install ns-3 (if not already installed)
# See: https://www.nsnam.org/docs/release/3.38/tutorial/html/getting-started.html
```

## Usage

### Running the Baseline Experiment
```bash
python -m src.experiments.run_experiment --config config/shippy_baseline.yaml
```

### Running Multi-Seed Experiments
```bash
python -m src.experiments.run_multi_seed --config config/shippy_baseline.yaml --seeds 20
```

### Analyzing Results
```bash
jupyter notebook notebooks/analyze_results.ipynb
```

## Configuration

Experiments are configured via YAML files in `config/`. See `config/shippy_baseline.yaml` for the baseline scenario.

---

## Experimental Methodology

### Baseline Scenario: ShippyCo Cold Chain
**Motivation**: Reefer container yard with 100 temperature sensors monitoring spoilage risk. Nodes must reach consensus on ambient temperature despite:
- Adversarial containers sending false readings to manipulate insurance claims
- LoRa Class A constraints (1% duty cycle, SF7-12, 125 kHz BW)
- Periodic ground truth changes (door openings → +3°C spikes)

**Parameters**:
```yaml
Network:
  N: 100                      # Sensor nodes
  Area: 1000m × 1000m         # Container yard
  Placement: grid-with-jitter # Realistic non-uniform density
  SF: 9                       # Spreading factor (typ. outdoor)
  BW: 125                     # kHz (LoRaWAN standard)
  CR: 4/5                     # Coding rate
  TxPower: 14 dBm             # Regulatory limit (US/EU)
  DutyCycle: 0.01             # 1% airtime cap (ETSI EN 300 220)
  WakeFraction: 0.5           # 50% async duty-cycling

Consensus:
  Epsilon: 1.0                # ±1°C agreement tolerance
  W0: 5.0                     # Initial CI width (±5°C uncertainty)
  NoiseSigma: 0.5             # Honest sensor std. dev.
  AcceptTau_IOU: 0.20         # 20% CI overlap required
  TrimT_min: 2                # Min trim/side (≥ local Byzantine fraction)
  TrimT_max: 0.20             # Max trim (20% of accepted values)
  Estimator: GeomMedian       # Default robust center
  LambdaMin: 0.08             # Minimum contraction/round
  LambdaMax: 0.18             # Maximum contraction/round

Adversarial:
  Beta: 0.10                  # 10% Byzantine nodes
  AttackMix:                  # Heterogeneous attacks
    - MIMIC: 50%              # IoU-passing bias injection
    - COLLIDER: 20%           # PHY-layer jamming
    - SPIKE: 20%              # +20°C outliers
    - DRIFT: 10%              # Slow bias accumulation

Ground Truth Dynamics:
  x*(t):
    - t ∈ [0, 1200s]:   25.0°C  (stable baseline)
    - t ∈ [1200, 1800s]: 28.0°C  (door open → heat ingress)
    - t > 1800s:         25.0°C  (door closed → return to baseline)
  ChangeDetection: CUSUM      # Trigger re-stabilization tracking

Experimental Control:
  Seeds: 20                   # Statistical confidence (95% CI)
  MaxRounds: 5000             # Safety termination
  RoundBudget_s: ~60s         # Expected round time (ns-3 measured)
```

### Comparative Baselines
We compare against:
1. **Classical Trimmed Mean** (no IoU acceptance, fixed λ)
2. **Geometric Median Only** (no adaptive λ)
3. **No Byzantine Defense** (vanilla averaging, to show attack impact)
4. **Ideal Network** (p_s = 1.0, no duty cycle, to isolate consensus vs. radio effects)

---

## Expected Results & Hypotheses

### H1: Radio Realism Dominates Convergence Time
**Prediction**: T_meas will be 3-5× longer than toy model predictions that ignore duty cycle and collisions.

**Validation**: Compare T_meas vs. T_pred with and without ns-3 traces. Plot gap ratio vs. SF (airtime increases exponentially with SF).

### H2: IoU Acceptance Bounds MIMIC Bias
**Prediction**: Under 10% MIMIC attackers, final bias ≤ 0.3°C (compared to >2°C for naive acceptance).

**Validation**: Track `|mean(CI_mid[honest]) - x*(t)|` over time. Show IoU+vote rejects >80% of MIMIC messages.

### H3: Adaptive λ Improves Convergence 2×
**Prediction**: Adaptive λ ∈ [0.08, 0.18] reaches ε-agreement in ~40 rounds vs. ~80 rounds for fixed λ = 0.08.

**Validation**: Plot rounds-to-convergence vs. λ_mode (fixed, adaptive-no-throttle, adaptive-full).

### H4: Continuous Tracking Reveals Re-Stabilization Cost
**Prediction**: After ground truth change at t=1200s, re-stabilization takes 15-25 rounds (vs. 40-50 from cold start).

**Validation**: Measure T_restab (exit ε-ball → re-enter) vs. initial T_conv. Show CUSUM detection latency < 5 rounds.

### H5: Partitions Degrade Global Consensus but Preserve Local
**Prediction**: Under 50% wake fraction, network partitions into 2-3 components. Each reaches local ε-agreement independently.

**Validation**: Plot per-component ε-agreement over time. Show `∀ components C: reach_eps(C) = True` even if global ≠ True.

---

## Related Work & Positioning

| Work | Byzantine Resilience | LPWAN Realism | Continuous Operation | Adaptive Mechanisms |
|------|---------------------|---------------|---------------------|---------------------|
| Tsitsiklis '84 | ✗ (averaging) | ✗ (sync rounds) | ✗ (one-shot) | ✗ |
| Vaidya '12 | ✓ (trimming) | ✗ (complete graph) | ✗ | ✗ |
| LeBlanc '13 | ✓ (geom. median) | ✗ (instant broadcast) | ✗ | ✗ |
| Sundaram '19 | ✓ (MoM) | ✗ (bounded delay) | ✗ | ✗ |
| **This Work** | ✓ (IoU+vote+robust est.) | ✓ (ns-3 LoRa) | ✓ (stability windows) | ✓ (adaptive λ, throttling) |

**Key Differentiators**:
- First to model **ALOHA collisions + duty cycle + Class A timing** in Byzantine consensus
- First to address **mimicry attacks** via scale-invariant acceptance
- First to track **continuous stability** rather than one-shot convergence

---

## Key Design Decisions & Trade-offs

### Why IoU over Fixed-Threshold Acceptance?
**Problem**: Fixed thresholds `|x_i - x_j| < τ` require tuning per scenario (temperature vs. pressure vs. humidity have different scales).

**Solution**: IoU is scale-invariant—threshold 0.20 works across domains.

**Trade-off**: Higher computation (interval arithmetic) vs. simpler comparison. We show overhead is <5% of round time.

### Why Geometric Median over Mean?
**Problem**: Trimmed mean fails under coordinated attacks where adversaries cluster just inside trim boundaries.

**Solution**: Geometric median has breakdown point ~0.5 (robust to 50% outliers).

**Trade-off**: Iterative Weiszfeld algorithm (10-20 iterations) vs. O(1) mean. For N=100 nodes, overhead <50ms/round.

### Why Adaptive λ?
**Problem**: Fixed λ_min is too slow in low-dispersion regimes. Fixed λ_max is unstable under attacks.

**Solution**: Map MAD(accepted_values) → λ ∈ [λ_min, λ_max] with throttling under weak support.

**Trade-off**: Adds one extra dispersion calculation per round (~O(n log n) sort). Negligible vs. network latency (seconds).

## License

Academic use only. See LICENSE file.

## Citation

```
@mastersthesis{larkin2025byzantine,
  author  = {Zachary Larkin},
  title   = {Byzantine-Resilient Consensus for LPWAN Networks},
  school  = {Vanderbilt University},
  year    = {2025}
}
```

