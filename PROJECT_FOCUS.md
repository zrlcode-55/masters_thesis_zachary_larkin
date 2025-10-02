# PROJECT FOCUS: RIGOROUS CS RESEARCH

**CRITICAL RULE**: This is a Computer Science PhD thesis, NOT an application demo.

---

## What This Project IS ✅

1. **Byzantine consensus algorithms** for LPWAN networks
2. **Novel mathematical contributions**: IoU acceptance, adaptive contraction, convergence bounds
3. **Rigorous parameter validation** against published research
4. **Algorithmic performance analysis** across parameter regimes
5. **Theoretical analysis** with empirical validation

---

## What This Project IS NOT ❌

1. **NOT** a shipping monitoring system
2. **NOT** a cold-chain application
3. **NOT** a product or deployment
4. **NOT** ShippyCo's solution
5. **NOT** domain-specific engineering

---

## Language We Use

### ✅ CORRECT (CS-Focused)
- "Byzantine consensus under packet loss"
- "IoU-based CI acceptance mechanism"
- "Convergence bound as function of p_s, T_pkt, λ"
- "Parameter ε defines consensus quality"
- "Step change in ground truth at t=1200s"
- "Configuration A: N=100, f=10%, G≈1.0"

### ❌ WRONG (Application-Focused)
- "ShippyCo baseline"
- "Container yard monitoring"
- "Door opens at 20 minutes"
- "Cold-chain parameters"
- "Reefer sensors"
- "Temperature monitoring"

---

## How to Frame Parameters

### ❌ WRONG:
```yaml
epsilon: 1.0  # Temperature tolerance for cold-chain
```

### ✅ CORRECT:
```yaml
epsilon: 1.0  # ε-agreement tolerance (consensus quality parameter)
# Chosen as representative value. Results validated across ε ∈ [0.5, 2.0]
```

---

## How to Name Scenarios

### ❌ WRONG:
- `shippy_baseline.yaml`
- `cold_chain_scenario.yaml`
- `container_monitoring.yaml`

### ✅ CORRECT:
- `baseline_100n_10b.yaml` (N=100, f=10% Byzantine)
- `scaling_200n.yaml` (Network scaling test)
- `security_20b.yaml` (High Byzantine fraction)

---

## README/Documentation Structure

### ✅ CORRECT ORDER:
1. **Abstract**: Byzantine consensus problem
2. **Novel Contributions**: IoU acceptance, adaptive λ, bounds
3. **Algorithmic Properties**: Convergence, stability, robustness
4. **Parameter Validation**: Citations for all values
5. **Experimental Results**: Performance across regimes
6. *(Optional, minimal)* Application example as footnote

### ❌ WRONG ORDER:
1. ShippyCo use case
2. Cold-chain monitoring requirements
3. Container deployment scenario
4. Our solution for shipping

---

## Test Naming

### ✅ CORRECT:
```python
def test_iou_defends_against_mimic():
    """IoU acceptance rejects MIMIC attacks (bias <0.5 vs >2.0 without)."""

def test_convergence_bound_tightness():
    """Theoretical bound predicts within 15% of measured convergence."""
```

### ❌ WRONG:
```python
def test_shippy_scenario():
    """Test cold-chain monitoring works."""
```

---

## Defense Prep

### Committee asks: "What is this research about?"

**❌ WRONG Answer:**
"We built a system for ShippyCo to monitor refrigerated containers..."

**✅ CORRECT Answer:**
"We develop Byzantine consensus algorithms for LPWAN networks with 85% packet loss. Our contributions are: (1) IoU-based acceptance to defend against mimicry attacks, proving bias reduction from >2.0 to <0.5; (2) adaptive contraction achieving 2× speedup; (3) radio-realistic convergence bounds accurate within 15%. We validate using parameters representative of distributed sensing systems."

### Committee asks: "Why these parameter values?"

**❌ WRONG Answer:**
"Because that's what cold-chain monitoring needs..."

**✅ CORRECT Answer:**
"ε=1.0 is representative for sensor networks. We validate via sensitivity analysis sweeping ε ∈ [0.5, 2.0], showing algorithmic improvements hold across the range. The specific value provides concrete instantiation for experiments, but contributions are parameter-independent [see Chapter 5, Figures 5.4-5.6]."

---

## Code Comments

### ✅ CORRECT:
```python
# ε-agreement tolerance: defines consensus quality
epsilon = 1.0

# Step change in ground truth (tests re-stabilization)
truth_change_time = 1200  # seconds
```

### ❌ WRONG:
```python
# Temperature tolerance for shipping containers
epsilon = 1.0

# Door opens (cold air enters)
door_open_time = 1200
```

---

## File Organization

```
✅ GOOD STRUCTURE:
config/scenarios/
  ├── baseline_100n_10b.yaml      # Primary validation
  ├── scaling_200n.yaml           # Network scaling
  ├── security_20b.yaml           # Byzantine stress
  └── sensitivity_sweep.yaml      # Parameter sweeps

❌ BAD STRUCTURE:
config/scenarios/
  ├── shippy_baseline.yaml
  ├── applications/
  │   └── cold_chain.yaml
```

---

## Summary

**REMEMBER**: 
- You're researching **Byzantine consensus algorithms**
- Applications are **validation contexts**, not research goals
- Parameters are **representative values**, not requirements
- Focus on **algorithmic contributions**, not use cases

**When in doubt, ask**: "Is this about the algorithm or the application?"
- If algorithm → Include prominently
- If application → Minimize or remove

---

**THIS IS CS RESEARCH. ACT LIKE IT.**

