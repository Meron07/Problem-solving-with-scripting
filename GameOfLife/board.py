"""
Board class for managing the Game of Life grid.
"""

import logging
from typing import List, Tuple, Optional
from .exceptions import InvalidDimensionError
from .metaprogramming import validate_grid, performance_monitor

logger = logging.getLogger(__name__)


class Board:
    """Manages the Game of Life grid state."""
    
    def __init__(self, width: int, height: int):
        """
        Initialize a board with given dimensions.
        
        Args:
            width: Width of the grid
            height: Height of the grid
            
        Raises:
            InvalidDimensionError: If dimensions are invalid
        """
        if width <= 0 or height <= 0:
            raise InvalidDimensionError(f"Dimensions must be positive, got {width}x{height}")
        
        if width > 1000 or height > 1000:
            raise InvalidDimensionError(f"Dimensions too large (max 1000x1000), got {width}x{height}")
        
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.generation = 0
        
        logger.info(f"Created board: {width}x{height}")
    
    @validate_grid
    def set_cell(self, row: int, col: int, value: int):
        """
        Set a cell value.
        
        Args:
            row: Row index
            col: Column index
            value: Cell value (0 or 1)
        """
        if not (0 <= row < self.height and 0 <= col < self.width):
            raise IndexError(f"Cell ({row}, {col}) out of bounds for {self.width}x{self.height} grid")
        
        if value not in (0, 1):
            raise ValueError(f"Cell value must be 0 or 1, got {value}")
        
        self.grid[row][col] = value
    
    @validate_grid
    def get_cell(self, row: int, col: int) -> int:
        """Get a cell value."""
        if not (0 <= row < self.height and 0 <= col < self.width):
            return 0  # Out of bounds cells are considered dead
        return self.grid[row][col]
    
    @validate_grid
    def count_neighbors(self, row: int, col: int) -> int:
        """
        Count live neighbors of a cell.
        
        Args:
            row: Row index
            col: Column index
            
        Returns:
            Number of live neighbors (0-8)
        """
        count = 0
        
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip the cell itself
                
                neighbor_row = row + dr
                neighbor_col = col + dc
                
                # Check bounds
                if (0 <= neighbor_row < self.height and
                    0 <= neighbor_col < self.width):
                    count += self.grid[neighbor_row][neighbor_col]
        
        return count
    
    @validate_grid
    def count_alive(self) -> int:
        """Count total number of alive cells."""
        return sum(sum(row) for row in self.grid)
    
    @validate_grid
    def clear(self):
        """Clear the board (set all cells to dead)."""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
        logger.info("Board cleared")
    
    @validate_grid
    def load_pattern(self, filename: str, offset_row: int = 0, offset_col: int = 0):
        """
        Load a pattern from file onto the board.
        
        Args:
            filename: Path to pattern file
            offset_row: Row offset for pattern placement
            offset_col: Column offset for pattern placement
        """
        from .pattern_parser import PatternParser
        
        pattern = PatternParser.parse(filename)
        
        for row, col in pattern['cells']:
            new_row = row + offset_row
            new_col = col + offset_col
            
            if 0 <= new_row < self.height and 0 <= new_col < self.width:
                self.grid[new_row][new_col] = 1
            else:
                logger.warning(f"Cell ({new_row}, {new_col}) from pattern out of bounds")
        
        logger.info(f"Loaded pattern from {filename} at offset ({offset_row}, {offset_col})")
    
    @validate_grid
    def to_string(self, alive_char: str = '█', dead_char: str = '·') -> str:
        """
        Convert board to string representation.
        
        Args:
            alive_char: Character for alive cells
            dead_char: Character for dead cells
            
        Returns:
            String representation of the board
        """
        lines = []
        for row in self.grid:
            line = ''.join(alive_char if cell else dead_char for cell in row)
            lines.append(line)
        return '\n'.join(lines)
    
    def __str__(self):
        return self.to_string()
    
    @validate_grid
    def copy(self) -> 'Board':
        """Create a deep copy of the board."""
        new_board = Board(self.width, self.height)
        new_board.grid = [row[:] for row in self.grid]
        new_board.generation = self.generation
        return new_board