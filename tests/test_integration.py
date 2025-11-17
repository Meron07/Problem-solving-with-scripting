"""
Integration test to verify end-to-end functionality.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_courier_imports():
    """Test that all CourierOptimizer modules can be imported."""
    from CourierOptimizer import CourierOptimizer, TransportMode, Delivery
    from CourierOptimizer.validator import DeliveryValidator
    from CourierOptimizer.distance import DistanceCalculator
    from CourierOptimizer.optimizer import CourierOptimizer
    from CourierOptimizer.transport import TransportModes
    from CourierOptimizer.file_handler import FileHandler
    
    assert CourierOptimizer is not None
    assert TransportMode is not None
    assert Delivery is not None


def test_game_of_life_imports():
    """Test that all GameOfLife modules can be imported."""
    from GameOfLife import Board, StandardRules, RuleRegistry, Simulator
    from GameOfLife.pattern_parser import PatternParser
    from GameOfLife.metaprogramming import RuleRegistry
    
    assert Board is not None
    assert StandardRules is not None
    assert Simulator is not None


if __name__ == '__main__':
    import pytest
    pytest.main([__file__, '-v'])