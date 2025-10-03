"""
Interval Arithmetic Primitives

Core operations on confidence intervals for consensus algorithms.

A confidence interval CI = [lower, upper] represents uncertainty in estimation.
We use interval arithmetic to:
1. Compute intersection and union for IoU filtering
2. Contract intervals during consensus
3. Check agreement (ε-consensus)
"""

import numpy as np
from typing import Tuple, List, Optional
from dataclasses import dataclass


@dataclass
class ConfidenceInterval:
    """
    Confidence interval representation.
    
    Attributes:
        lower: Lower bound
        upper: Upper bound
        midpoint: Center point (computed)
        width: Full width (computed)
        half_width: Half-width from midpoint (computed)
    """
    lower: float
    upper: float
    
    def __post_init__(self):
        """Validate interval."""
        if self.lower > self.upper:
            raise ValueError(f"Invalid interval: [{self.lower}, {self.upper}]")
    
    @property
    def midpoint(self) -> float:
        """Center of interval."""
        return (self.lower + self.upper) / 2
    
    @property
    def width(self) -> float:
        """Full width of interval."""
        return self.upper - self.lower
    
    @property
    def half_width(self) -> float:
        """Half-width (radius)."""
        return self.width / 2
    
    def contains(self, value: float) -> bool:
        """Check if value is in interval."""
        return self.lower <= value <= self.upper
    
    def __repr__(self) -> str:
        return f"CI([{self.lower:.3f}, {self.upper:.3f}], mid={self.midpoint:.3f}, w={self.width:.3f})"


def interval_intersection(ci1: ConfidenceInterval, ci2: ConfidenceInterval) -> Optional[ConfidenceInterval]:
    """
    Compute intersection of two intervals.
    
    Args:
        ci1, ci2: Confidence intervals
        
    Returns:
        Intersection interval, or None if disjoint
        
    Example:
        >>> ci1 = ConfidenceInterval(1.0, 3.0)
        >>> ci2 = ConfidenceInterval(2.0, 4.0)
        >>> intersection = interval_intersection(ci1, ci2)
        >>> intersection.lower, intersection.upper
        (2.0, 3.0)
    """
    lower = max(ci1.lower, ci2.lower)
    upper = min(ci1.upper, ci2.upper)
    
    if lower > upper:
        return None  # Disjoint
    
    return ConfidenceInterval(lower, upper)


def interval_union(ci1: ConfidenceInterval, ci2: ConfidenceInterval) -> ConfidenceInterval:
    """
    Compute union (hull) of two intervals.
    
    Note: This returns the convex hull [min, max], not strict union.
    
    Args:
        ci1, ci2: Confidence intervals
        
    Returns:
        Union interval (smallest interval containing both)
        
    Example:
        >>> ci1 = ConfidenceInterval(1.0, 2.0)
        >>> ci2 = ConfidenceInterval(3.0, 4.0)
        >>> union = interval_union(ci1, ci2)
        >>> union.lower, union.upper
        (1.0, 4.0)
    """
    lower = min(ci1.lower, ci2.lower)
    upper = max(ci1.upper, ci2.upper)
    return ConfidenceInterval(lower, upper)


def compute_iou(ci1: ConfidenceInterval, ci2: ConfidenceInterval) -> float:
    """
    Compute Intersection-over-Union (IoU) of two confidence intervals.
    
    IoU = |CI_1 ∩ CI_2| / |CI_1 ∪ CI_2|
    
    Properties:
    - IoU ∈ [0, 1]
    - IoU = 0 if disjoint
    - IoU = 1 if identical
    - Scale-invariant (works for temperature, pressure, etc.)
    
    Args:
        ci1, ci2: Confidence intervals
        
    Returns:
        IoU score ∈ [0, 1]
        
    Example:
        >>> ci1 = ConfidenceInterval(0.0, 2.0)  # [0, 2]
        >>> ci2 = ConfidenceInterval(1.0, 3.0)  # [1, 3]
        >>> compute_iou(ci1, ci2)
        0.333...  # intersection [1,2] has width 1, union [0,3] has width 3
    """
    intersection = interval_intersection(ci1, ci2)
    union = interval_union(ci1, ci2)
    
    if intersection is None:
        return 0.0
    
    # Avoid division by zero
    if union.width < 1e-12:
        return 1.0 if ci1.width < 1e-12 and ci2.width < 1e-12 else 0.0
    
    iou = intersection.width / union.width
    return np.clip(iou, 0.0, 1.0)


def contract_interval(ci: ConfidenceInterval, lambda_factor: float, target: Optional[float] = None) -> ConfidenceInterval:
    """
    Contract confidence interval toward target (or midpoint).
    
    New_CI = CI_mid + λ(CI - CI_mid)
    
    This is the core consensus operation: nodes shrink uncertainty.
    
    Args:
        ci: Current confidence interval
        lambda_factor: Contraction factor λ ∈ [0, 1]
            λ = 0: No contraction
            λ = 1: Collapse to point
        target: Contraction target (default: ci.midpoint)
        
    Returns:
        Contracted interval
        
    Example:
        >>> ci = ConfidenceInterval(0.0, 4.0)  # Mid = 2.0, width = 4.0
        >>> contracted = contract_interval(ci, lambda_factor=0.5)
        >>> contracted.midpoint, contracted.width
        (2.0, 2.0)  # Width reduced by λ=0.5
    """
    if not 0 <= lambda_factor <= 1:
        raise ValueError(f"λ must be in [0,1], got {lambda_factor}")
    
    center = target if target is not None else ci.midpoint
    new_half_width = ci.half_width * (1 - lambda_factor)
    
    return ConfidenceInterval(
        lower=center - new_half_width,
        upper=center + new_half_width
    )


def check_epsilon_agreement(intervals: List[ConfidenceInterval], epsilon: float) -> bool:
    """
    Check if all intervals satisfy ε-agreement.
    
    ε-agreement: max_{i,j} |mid_i - mid_j| ≤ ε AND all widths ≤ ε
    
    Args:
        intervals: List of confidence intervals
        epsilon: Agreement tolerance
        
    Returns:
        True if ε-agreement achieved
        
    Example:
        >>> cis = [
        ...     ConfidenceInterval(24.0, 26.0),  # mid=25
        ...     ConfidenceInterval(24.5, 25.5),  # mid=25
        ...     ConfidenceInterval(24.8, 25.2),  # mid=25
        ... ]
        >>> check_epsilon_agreement(cis, epsilon=1.0)
        True  # All midpoints within 1.0
    """
    if not intervals:
        return True
    
    midpoints = [ci.midpoint for ci in intervals]
    widths = [ci.width for ci in intervals]
    
    # Check pairwise midpoint agreement
    max_disagreement = max(midpoints) - min(midpoints)
    if max_disagreement > epsilon:
        return False
    
    # Check all widths below epsilon (optional, depending on definition)
    # For now, we only check midpoint agreement
    
    return True


def create_interval_from_samples(samples: np.ndarray, confidence: float = 0.95) -> ConfidenceInterval:
    """
    Create confidence interval from data samples.
    
    Args:
        samples: Observed data points
        confidence: Coverage probability (e.g., 0.95 for 95% CI)
        
    Returns:
        Confidence interval
        
    Note:
        This uses empirical quantiles. For sub-Gaussian noise, could use
        theoretical bounds instead.
    """
    alpha = (1 - confidence) / 2
    lower = np.quantile(samples, alpha)
    upper = np.quantile(samples, 1 - alpha)
    return ConfidenceInterval(lower, upper)


# Batch operations
def compute_iou_matrix(intervals: List[ConfidenceInterval]) -> np.ndarray:
    """
    Compute pairwise IoU matrix for all intervals.
    
    Useful for graph-based consensus analysis.
    
    Args:
        intervals: List of confidence intervals
        
    Returns:
        n×n matrix where M[i,j] = IoU(intervals[i], intervals[j])
    """
    n = len(intervals)
    iou_matrix = np.zeros((n, n))
    
    for i in range(n):
        for j in range(n):
            iou_matrix[i, j] = compute_iou(intervals[i], intervals[j])
    
    return iou_matrix


if __name__ == "__main__":
    print("=" * 70)
    print("INTERVAL ARITHMETIC PRIMITIVES - VALIDATION")
    print("=" * 70)
    
    # Example: IoU computation
    print("\n1. IoU Computation:")
    ci1 = ConfidenceInterval(24.0, 26.0)  # [24, 26], mid=25
    ci2 = ConfidenceInterval(25.0, 27.0)  # [25, 27], mid=26
    iou = compute_iou(ci1, ci2)
    print(f"   {ci1}")
    print(f"   {ci2}")
    print(f"   IoU = {iou:.3f}")
    
    # Example: Contraction
    print("\n2. Interval Contraction:")
    ci = ConfidenceInterval(20.0, 30.0)
    print(f"   Original: {ci}")
    contracted = contract_interval(ci, lambda_factor=0.3)
    print(f"   After λ=0.3 contraction: {contracted}")
    
    # Example: Epsilon-agreement
    print("\n3. ε-Agreement Check:")
    intervals = [
        ConfidenceInterval(24.5, 25.5),
        ConfidenceInterval(24.7, 25.3),
        ConfidenceInterval(24.6, 25.4)
    ]
    epsilon = 0.5
    agreed = check_epsilon_agreement(intervals, epsilon)
    print(f"   Intervals: {[ci.midpoint for ci in intervals]}")
    print(f"   ε = {epsilon}")
    print(f"   Agreement: {agreed}")
    
    print("\n" + "=" * 70)

