"""
Simulator class for running Game of Life simulations.
"""

import logging
import time
from typing import Optional, Callable, Tuple
from .board import Board
from .rules import StandardRules
from .metaprogramming import RuleRegistry, performance_monitor
from .exceptions import SimulationOverflowError

logger = logging.getLogger(__name__)


class Simulator:
    """Manages Game of Life simulation execution."""
    
    def __init__(self, board: Board, rule_name: str = 'standard'):
        """
        Initialize simulator with a board and rule set.
        
        Args:
            board: Initial board state
            rule_name: Name of registered rule to use
        """
        self.board = board
        self.rule_class = RuleRegistry.get_rule(rule_name)
        self.rule_name = rule_name
        self.history = []
        self.max_generations = 10000
        
        logger.info(f"Initialized simulator with {rule_name} rules")
    
    @performance_monitor
    def step(self) -> Board:
        """
        Evolve the board by one generation.
        
        Returns:
            The evolved board
        """
        self.board = self.rule_class.evolve(self.board)
        return self.board
    
    @performance_monitor
    def run(self, generations: int, 
            callback: Optional[Callable[[Board, int], None]] = None,
            save_history: bool = False) -> Board:
        """
        Run simulation for specified number of generations.
        
        Args:
            generations: Number of generations to simulate
            callback: Optional callback function called after each generation
            save_history: Whether to save board states in history
            
        Returns:
            Final board state
            
        Raises:
            SimulationOverflowError: If generations exceeds maximum
        """
        if generations > self.max_generations:
            raise SimulationOverflowError(
                f"Requested {generations} generations exceeds maximum {self.max_generations}"
            )
        
        logger.info(f"Running simulation for {generations} generations")
        
        if save_history:
            self.history = [self.board.copy()]
        
        for gen in range(generations):
            self.step()
            
            if callback:
                callback(self.board, gen + 1)
            
            if save_history:
                self.history.append(self.board.copy())
            
            # Check for extinction
            if self.board.count_alive() == 0:
                logger.info(f"Simulation ended at generation {self.board.generation} (extinction)")
                break
        
        logger.info(f"Simulation completed at generation {self.board.generation}")
        
        return self.board
    
    def run_until_stable(self, max_generations: Optional[int] = None,
                        check_period: int = 1) -> Tuple[Board, str]:
        """
        Run simulation until a stable state is detected.
        
        Detects:
        - Still life (no change)
        - Oscillators (periodic patterns)
        - Extinction (no alive cells)
        
        Args:
            max_generations: Maximum generations to run
            check_period: How often to check for stability
            
        Returns:
            Tuple of (final board, stability type)
        """
        if max_generations is None:
            max_generations = self.max_generations
        
        previous_states = []
        
        for gen in range(max_generations):
            prev_grid = [row[:] for row in self.board.grid]
            self.step()
            
            # Check for extinction
            if self.board.count_alive() == 0:
                return self.board, "extinction"
            
            # Check for still life
            if self.board.grid == prev_grid:
                return self.board, "still_life"
            
            # Check for oscillators (period up to 100)
            if gen % check_period == 0:
                for i, state in enumerate(previous_states[-100:]):
                    if self.board.grid == state:
                        period = len(previous_states) - i
                        logger.info(f"Detected oscillator with period {period}")
                        return self.board, f"oscillator_period_{period}"
                
                previous_states.append([row[:] for row in self.board.grid])
        
        return self.board, "max_generations_reached"
    
    def reset(self, board: Optional[Board] = None):
        """
        Reset simulator with a new board.
        
        Args:
            board: New board to use (or None to clear history only)
        """
        if board:
            self.board = board
        self.history = []
        logger.info("Simulator reset")
    
    def get_statistics(self) -> dict:
        """
        Get current simulation statistics.
        
        Returns:
            Dictionary with statistics
        """
        return {
            'generation': self.board.generation,
            'alive_cells': self.board.count_alive(),
            'dead_cells': (self.board.width * self.board.height) - self.board.count_alive(),
            'density': self.board.count_alive() / (self.board.width * self.board.height),
            'rule': self.rule_name,
            'board_size': f"{self.board.width}x{self.board.height}"
        }


from typing import Tuple