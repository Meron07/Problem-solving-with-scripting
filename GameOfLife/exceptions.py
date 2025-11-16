"""
Custom exceptions for Game of Life simulator.
"""


class GameOfLifeError(Exception):
    """Base exception for Game of Life simulator."""
    pass


class InvalidDimensionError(GameOfLifeError):
    """Raised when grid dimensions are invalid."""
    pass


class InvalidPatternError(GameOfLifeError):
    """Raised when pattern file is malformed."""
    pass


class SimulationOverflowError(GameOfLifeError):
    """Raised when simulation exceeds limits."""
    pass


class PatternParseError(GameOfLifeError):
    """Raised when pattern parsing fails."""
    pass


class FileHandlingError(GameOfLifeError):
    """Raised when file operations fail."""
    pass