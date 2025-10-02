"""
Ground truth models for consensus experiments.

Implements time-varying ground truth with change detection scenarios
(e.g., reefer door openings, temperature changes).
"""

from abc import ABC, abstractmethod
from typing import List, Tuple
from dataclasses import dataclass


@dataclass
class GroundTruthChange:
    """Represents a change in ground truth at a specific time."""
    time: float  # seconds
    value: float  # new truth value


class GroundTruth(ABC):
    """
    Abstract base class for ground truth models.
    
    Ground truth x*(t) represents the true value being estimated
    by the sensor network (e.g., ambient temperature in container yard).
    """
    
    @abstractmethod
    def get_value(self, time: float) -> float:
        """
        Get ground truth value at specified time.
        
        Args:
            time: Simulation time in seconds
            
        Returns:
            True value at time t
        """
        pass
    
    @abstractmethod
    def get_changes(self) -> List[GroundTruthChange]:
        """
        Get list of ground truth changes.
        
        Returns:
            List of change events (time, new_value)
        """
        pass


class PiecewiseGroundTruth(GroundTruth):
    """
    Piecewise-constant ground truth model.
    
    Models scenarios where ground truth changes at specific times:
    - Reefer door opens → temperature increases
    - Door closes → temperature returns to baseline
    - Environmental changes in IoT deployments
    
    Example:
        >>> # Temperature in container yard
        >>> changes = [
        ...     GroundTruthChange(time=0, value=25.0),      # Baseline
        ...     GroundTruthChange(time=1200, value=28.0),   # Door open
        ...     GroundTruthChange(time=1800, value=25.0),   # Door closed
        ... ]
        >>> truth = PiecewiseGroundTruth(changes)
        >>> truth.get_value(600)   # 25.0 (before change)
        >>> truth.get_value(1500)  # 28.0 (during open)
        >>> truth.get_value(2000)  # 25.0 (after close)
    """
    
    def __init__(self, changes: List[GroundTruthChange]):
        """
        Initialize piecewise constant ground truth.
        
        Args:
            changes: List of (time, value) changes, must be sorted by time
        """
        if not changes:
            raise ValueError("Must provide at least one ground truth value")
        
        # Sort by time
        self.changes = sorted(changes, key=lambda c: c.time)
        
        # Validate times are non-negative
        if any(c.time < 0 for c in self.changes):
            raise ValueError("Change times must be non-negative")
    
    def get_value(self, time: float) -> float:
        """
        Get ground truth at specified time.
        
        Uses the most recent change before or at the given time.
        """
        # Find the most recent change <= time
        current_value = self.changes[0].value
        
        for change in self.changes:
            if change.time <= time:
                current_value = change.value
            else:
                break
        
        return current_value
    
    def get_changes(self) -> List[GroundTruthChange]:
        """Get list of all changes."""
        return self.changes.copy()
    
    def get_next_change_time(self, current_time: float) -> float:
        """
        Get time of next ground truth change after current_time.
        
        Args:
            current_time: Current simulation time
            
        Returns:
            Time of next change, or float('inf') if no more changes
        """
        for change in self.changes:
            if change.time > current_time:
                return change.time
        return float('inf')
    
    def has_changed_since(self, last_check_time: float, current_time: float) -> bool:
        """
        Check if ground truth changed in time interval.
        
        Args:
            last_check_time: Start of interval
            current_time: End of interval
            
        Returns:
            True if ground truth changed during [last_check_time, current_time]
        """
        for change in self.changes:
            if last_check_time < change.time <= current_time:
                return True
        return False
    
    def __repr__(self) -> str:
        return (
            f"PiecewiseGroundTruth("
            f"baseline={self.changes[0].value}, "
            f"changes={len(self.changes)-1})"
        )


class ConstantGroundTruth(GroundTruth):
    """
    Constant ground truth (no changes).
    
    Useful for baseline experiments without environmental dynamics.
    """
    
    def __init__(self, value: float):
        """
        Initialize constant ground truth.
        
        Args:
            value: Constant true value
        """
        self.value = value
        self._change = GroundTruthChange(time=0.0, value=value)
    
    def get_value(self, time: float) -> float:
        """Always returns the same value."""
        return self.value
    
    def get_changes(self) -> List[GroundTruthChange]:
        """Returns single baseline value."""
        return [self._change]
    
    def __repr__(self) -> str:
        return f"ConstantGroundTruth(value={self.value})"

