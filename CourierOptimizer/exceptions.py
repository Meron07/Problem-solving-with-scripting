"""
Custom exceptions for CourierOptimizer package.
"""


class CourierOptimizerError(Exception):
    """Base exception for CourierOptimizer package."""
    pass


class ValidationError(CourierOptimizerError):
    """Raised when data validation fails."""
    pass


class InvalidCoordinateError(ValidationError):
    """Raised when coordinates are invalid."""
    pass


class InvalidPriorityError(ValidationError):
    """Raised when priority value is invalid."""
    pass


class InvalidWeightError(ValidationError):
    """Raised when weight value is invalid."""
    pass


class EmptyDataError(CourierOptimizerError):
    """Raised when no valid delivery data is available."""
    pass


class OptimizationError(CourierOptimizerError):
    """Raised when optimization process fails."""
    pass