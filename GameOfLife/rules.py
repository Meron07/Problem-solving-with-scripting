"""
Evolution rules for Game of Life.
"""

import logging
from typing import List
from .board import Board
from .metaprogramming import RuleRegistry, generation_counter, performance_monitor

logger = logging.getLogger(__name__)


@RuleRegistry.register('standard')
class StandardRules:
    """
    Standard Conway's Game of Life rules:
    1. Any live cell with 2 or 3 live neighbors survives
    2. Any dead cell with exactly 3 live neighbors becomes alive
    3. All other cells die or stay dead
    """
    
    @staticmethod
    @performance_monitor
    @generation_counter
    def evolve(board: Board) -> Board:
        """
        Evolve the board by one generation.
        
        Args:
            board: Current board state
            
        Returns:
            New board with evolved state
        """
        new_board = Board(board.width, board.height)
        new_board.generation = board.generation + 1
        
        for row in range(board.height):
            for col in range(board.width):
                current_state = board.get_cell(row, col)
                neighbors = board.count_neighbors(row, col)
                
                # Apply rules
                if current_state == 1:
                    # Cell is alive
                    if neighbors in (2, 3):
                        new_board.set_cell(row, col, 1)  # Survives
                    else:
                        new_board.set_cell(row, col, 0)  # Dies
                else:
                    # Cell is dead
                    if neighbors == 3:
                        new_board.set_cell(row, col, 1)  # Becomes alive
                    else:
                        new_board.set_cell(row, col, 0)  # Stays dead
        
        logger.debug(f"Evolved to generation {new_board.generation}")
        return new_board


@RuleRegistry.register('highlife')
class HighLifeRules:
    """
    HighLife variation:
    - Standard rules plus: dead cells with 6 neighbors come alive
    """
    
    @staticmethod
    @performance_monitor
    def evolve(board: Board) -> Board:
        """Evolve board using HighLife rules."""
        new_board = Board(board.width, board.height)
        new_board.generation = board.generation + 1
        
        for row in range(board.height):
            for col in range(board.width):
                current_state = board.get_cell(row, col)
                neighbors = board.count_neighbors(row, col)
                
                if current_state == 1:
                    if neighbors in (2, 3):
                        new_board.set_cell(row, col, 1)
                else:
                    if neighbors in (3, 6):
                        new_board.set_cell(row, col, 1)
        
        return new_board


@RuleRegistry.register('day_and_night')
class DayAndNightRules:
    """
    Day and Night variation:
    - Birth: 3, 6, 7, 8 neighbors
    - Survival: 3, 4, 6, 7, 8 neighbors
    """
    
    @staticmethod
    @performance_monitor
    def evolve(board: Board) -> Board:
        """Evolve board using Day and Night rules."""
        new_board = Board(board.width, board.height)
        new_board.generation = board.generation + 1
        
        for row in range(board.height):
            for col in range(board.width):
                current_state = board.get_cell(row, col)
                neighbors = board.count_neighbors(row, col)
                
                if current_state == 1:
                    if neighbors in (3, 4, 6, 7, 8):
                        new_board.set_cell(row, col, 1)
                else:
                    if neighbors in (3, 6, 7, 8):
                        new_board.set_cell(row, col, 1)
        
        return new_board


def evolve_grid(grid: List[List[int]]) -> List[List[int]]:
    """
    Helper function to evolve a raw grid using standard rules.
    Used for testing compatibility.
    
    Args:
        grid: 2D list representing the grid
        
    Returns:
        New evolved grid
    """
    height = len(grid)
    width = len(grid[0]) if grid else 0
    
    board = Board(width, height)
    board.grid = [row[:] for row in grid]
    
    evolved_board = StandardRules.evolve(board)
    
    return evolved_board.grid