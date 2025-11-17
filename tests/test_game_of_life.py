"""
Test suite for Game of Life simulator.
"""

import pytest
import os
from GameOfLife.board import Board
from GameOfLife.rules import evolve_grid, StandardRules, HighLifeRules
from GameOfLife.simulator import Simulator
from GameOfLife.metaprogramming import RuleRegistry
from GameOfLife.exceptions import (
    InvalidDimensionError, InvalidPatternError,
    SimulationOverflowError
)


class TestBoard:
    """Test Board class."""
    
    def test_board_init(self):
        """Test board initialization."""
        board = Board(10, 10)
        assert len(board.grid) == 10
        assert all(all(cell == 0 for cell in row) for row in board.grid)
        assert board.width == 10
        assert board.height == 10
        assert board.generation == 0
    
    def test_board_invalid_dimensions(self):
        """Test board with invalid dimensions."""
        with pytest.raises(InvalidDimensionError):
            Board(0, 10)
        
        with pytest.raises(InvalidDimensionError):
            Board(10, -5)
        
        with pytest.raises(InvalidDimensionError):
            Board(2000, 2000)  # Too large
    
    def test_set_cell(self):
        """Test setting cell values."""
        board = Board(5, 5)
        board.set_cell(2, 3, 1)
        assert board.grid[2][3] == 1
        assert board.get_cell(2, 3) == 1
    
    def test_set_cell_invalid(self):
        """Test setting cell with invalid coordinates."""
        board = Board(5, 5)
        
        with pytest.raises(IndexError):
            board.set_cell(10, 10, 1)
        
        with pytest.raises(ValueError):
            board.set_cell(2, 2, 5)  # Invalid value
    
    def test_count_neighbors(self):
        """Test neighbor counting."""
        board = Board(5, 5)
        
        # Create a pattern
        board.set_cell(1, 1, 1)
        board.set_cell(1, 2, 1)
        board.set_cell(2, 1, 1)
        
        # Center cell (2, 2) should have 3 neighbors
        assert board.count_neighbors(2, 2) == 3
        
        # Cell (1, 1) should have 1 neighbor
        assert board.count_neighbors(1, 1) == 1
    
    def test_count_alive(self):
        """Test counting alive cells."""
        board = Board(5, 5)
        assert board.count_alive() == 0
        
        board.set_cell(1, 1, 1)
        board.set_cell(2, 2, 1)
        assert board.count_alive() == 2
    
    def test_clear(self):
        """Test clearing the board."""
        board = Board(5, 5)
        board.set_cell(1, 1, 1)
        board.set_cell(2, 2, 1)
        
        board.clear()
        assert board.count_alive() == 0
        assert board.generation == 0
    
    def test_to_string(self):
        """Test string representation."""
        board = Board(3, 3)
        board.set_cell(1, 1, 1)
        
        string_repr = board.to_string(alive_char='O', dead_char='.')
        assert 'O' in string_repr
        assert '.' in string_repr
    
    def test_copy(self):
        """Test board copying."""
        board = Board(5, 5)
        board.set_cell(2, 2, 1)
        board.generation = 5
        
        copy = board.copy()
        assert copy.grid == board.grid
        assert copy.generation == board.generation
        assert copy is not board  # Different object


class TestRules:
    """Test evolution rules."""
    
    def test_evolve_grid_blinker(self):
        """Test blinker pattern (oscillator with period 2)."""
        # Horizontal blinker
        grid = [
            [0, 0, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, 0]
        ]
        
        # Evolve once - should become vertical
        new_grid = evolve_grid(grid)
        assert new_grid[2][1] == 1
        assert new_grid[2][2] == 1
        assert new_grid[2][3] == 1
        
        # Evolve again - should return to horizontal
        final_grid = evolve_grid(new_grid)
        assert final_grid == grid
    
    def test_evolve_grid_block(self):
        """Test block pattern (still life)."""
        grid = [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0]
        ]
        
        new_grid = evolve_grid(grid)
        assert new_grid == grid  # Block should not change
    
    def test_standard_rules(self):
        """Test StandardRules class."""
        board = Board(5, 5)
        board.set_cell(1, 1, 1)
        board.set_cell(1, 2, 1)
        board.set_cell(1, 3, 1)
        
        new_board = StandardRules.evolve(board)
        assert new_board.generation == 1
        assert new_board.count_alive() > 0
    
    def test_highlife_rules(self):
        """Test HighLife rules."""
        board = Board(5, 5)
        board.set_cell(2, 2, 1)
        
        # Surround with 6 neighbors
        for dr, dc in [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,0)]:
            board.set_cell(2+dr, 2+dc, 1)
        
        new_board = HighLifeRules.evolve(board)
        # With HighLife, cells with 6 neighbors can be born
        assert new_board is not None


class TestSimulator:
    """Test Simulator class."""
    
    def test_simulator_init(self):
        """Test simulator initialization."""
        board = Board(10, 10)
        simulator = Simulator(board)
        
        assert simulator.board == board
        assert simulator.rule_name == 'standard'
    
    def test_simulator_step(self):
        """Test single step evolution."""
        board = Board(5, 5)
        board.set_cell(1, 1, 1)
        board.set_cell(1, 2, 1)
        board.set_cell(1, 3, 1)
        
        simulator = Simulator(board)
        initial_gen = board.generation
        
        simulator.step()
        assert simulator.board.generation == initial_gen + 1
    
    def test_simulator_run(self):
        """Test running multiple generations."""
        board = Board(10, 10)
        board.set_cell(5, 5, 1)
        board.set_cell(5, 6, 1)
        board.set_cell(5, 7, 1)
        
        simulator = Simulator(board)
        final_board = simulator.run(10)
        
        assert final_board.generation == 10
    
    def test_simulator_run_overflow(self):
        """Test simulation overflow protection."""
        board = Board(10, 10)
        simulator = Simulator(board)
        
        with pytest.raises(SimulationOverflowError):
            simulator.run(20000)  # Exceeds maximum
    
    def test_simulator_run_until_stable_extinction(self):
        """Test running until extinction."""
        board = Board(5, 5)
        board.set_cell(2, 2, 1)  # Single cell will die
        
        simulator = Simulator(board)
        final_board, stability = simulator.run_until_stable(100)
        
        assert stability == "extinction"
        assert final_board.count_alive() == 0
    
    def test_simulator_run_until_stable_still_life(self):
        """Test running until still life."""
        board = Board(5, 5)
        # Create block (still life)
        board.set_cell(2, 2, 1)
        board.set_cell(2, 3, 1)
        board.set_cell(3, 2, 1)
        board.set_cell(3, 3, 1)
        
        simulator = Simulator(board)
        final_board, stability = simulator.run_until_stable(100)
        
        assert "still_life" in stability
    
    def test_simulator_reset(self):
        """Test simulator reset."""
        board = Board(5, 5)
        simulator = Simulator(board)
        
        simulator.run(5)
        simulator.reset()
        
        assert len(simulator.history) == 0
    
    def test_simulator_statistics(self):
        """Test statistics gathering."""
        board = Board(10, 10)
        board.set_cell(5, 5, 1)
        
        simulator = Simulator(board)
        stats = simulator.get_statistics()
        
        assert 'generation' in stats
        assert 'alive_cells' in stats
        assert 'density' in stats
        assert stats['alive_cells'] == 1


class TestRuleRegistry:
    """Test dynamic rule registration."""
    
    def test_rule_registry_get_standard(self):
        """Test getting standard rule."""
        rule = RuleRegistry.get_rule('standard')
        assert rule == StandardRules
    
    def test_rule_registry_list(self):
        """Test listing available rules."""
        rules = RuleRegistry.list_rules()
        assert 'standard' in rules
        assert isinstance(rules, list)
    
    def test_rule_registry_add_dynamic(self):
        """Test dynamically adding a rule."""
        def custom_evolve(board):
            # Simple custom rule
            return board.copy()
        
        RuleRegistry.add_rule_dynamically('custom_test', custom_evolve)
        
        rule = RuleRegistry.get_rule('custom_test')
        assert rule is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])