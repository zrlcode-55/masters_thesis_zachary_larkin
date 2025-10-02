"""
Honest sensor model with Gaussian noise.

Implements y_i(t) = x*(t) + N(0, σ²) where x*(t) is ground truth.
"""

import numpy as np
from typing import Optional

from .ground_truth import GroundTruth


class HonestSensor:
    """
    Honest sensor with additive Gaussian noise.
    
    Models realistic sensor behavior:
        y_i(t) = x*(t) + ε_i(t)
        where ε_i ~ N(0, σ²)
    
    Args:
        sensor_id: Unique sensor identifier
        ground_truth: Ground truth model
        noise_std: Standard deviation of measurement noise (σ)
        seed: Random seed for reproducibility
        
    Example:
        >>> from sensors import PiecewiseGroundTruth, GroundTruthChange
        >>> truth = PiecewiseGroundTruth([GroundTruthChange(0, 25.0)])
        >>> sensor = HonestSensor(0, truth, noise_std=0.5, seed=42)
        >>> reading = sensor.read(time=100.0)
        >>> abs(reading - 25.0) < 2.0  # Within ~4σ with high probability
        True
    """
    
    def __init__(
        self,
        sensor_id: int,
        ground_truth: GroundTruth,
        noise_std: float = 0.5,
        seed: Optional[int] = None
    ):
        """Initialize honest sensor."""
        self.sensor_id = sensor_id
        self.ground_truth = ground_truth
        self.noise_std = noise_std
        
        # Each sensor gets its own RNG for independent noise
        if seed is not None:
            self.rng = np.random.RandomState(seed + sensor_id)
        else:
            self.rng = np.random.RandomState()
        
        # Statistics
        self.num_readings = 0
        self.last_reading = None
        self.last_time = None
    
    def read(self, time: float) -> float:
        """
        Take a sensor reading at specified time.
        
        Args:
            time: Simulation time in seconds
            
        Returns:
            Noisy measurement y_i(t) = x*(t) + N(0, σ²)
        """
        # Get ground truth
        true_value = self.ground_truth.get_value(time)
        
        # Add Gaussian noise
        noise = self.rng.normal(0, self.noise_std)
        measurement = true_value + noise
        
        # Update statistics
        self.num_readings += 1
        self.last_reading = measurement
        self.last_time = time
        
        return measurement
    
    def get_confidence_interval(self, measurement: float, width_multiplier: float = 2.0) -> tuple:
        """
        Construct confidence interval around measurement.
        
        Args:
            measurement: Current reading
            width_multiplier: CI half-width as multiple of σ (default: 2σ ≈ 95%)
            
        Returns:
            (lower_bound, upper_bound) tuple
        """
        half_width = width_multiplier * self.noise_std
        return (measurement - half_width, measurement + half_width)
    
    def reset(self):
        """Reset sensor statistics."""
        self.num_readings = 0
        self.last_reading = None
        self.last_time = None
    
    def __repr__(self) -> str:
        return (
            f"HonestSensor(id={self.sensor_id}, "
            f"σ={self.noise_std}, "
            f"readings={self.num_readings})"
        )

