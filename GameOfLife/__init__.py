"""
GameOfLife package for simulating Conway's Game of Life.
Supports pattern loading, custom rules, and state management.
"""

from .board import Board
from .rules import StandardRules
from .metaprogramming import RuleRegistry
from .simulator import Simulator

__all__ = ['Board', 'StandardRules', 'RuleRegistry', 'Simulator']
__version__ = '1.0.0'