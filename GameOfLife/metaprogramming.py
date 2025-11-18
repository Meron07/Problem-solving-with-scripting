"""
Metaprogramming utilities for Game of Life.
Includes decorators and dynamic class modification.
"""

import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def performance_monitor(func):
    """Decorator to monitor performance of functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.debug(f"{func.__name__} took {elapsed:.4f} seconds")
        return result
    return wrapper


def generation_counter(func):
    """Decorator to count generations evolved."""
    count = {'value': 0}
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        count['value'] += 1
        logger.debug(f"Generation {count['value']}")
        return func(*args, **kwargs)
    
    wrapper.generation_count = count
    return wrapper


def validate_grid(func):
    """Decorator to validate grid state before operations."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not hasattr(self, 'grid') or self.grid is None:
            raise ValueError("Grid not initialized")
        return func(self, *args, **kwargs)
    return wrapper


class RuleRegistry:
    """
    Registry for dynamically adding and managing evolution rules.
    Demonstrates metaprogramming through dynamic class modification.
    """
    
    _rules = {}
    
    @classmethod
    def register(cls, name: str):
        """
        Decorator to register a rule class.
        
        Usage:
            @RuleRegistry.register('custom')
            class CustomRule:
                @staticmethod
                def evolve(grid):
                    ...
        """
        def decorator(rule_class):
            cls._rules[name] = rule_class
            logger.info(f"Registered rule: {name}")
            return rule_class
        return decorator
    
    @classmethod
    def get_rule(cls, name: str):
        """Get a registered rule by name."""
        if name not in cls._rules:
            raise ValueError(f"Rule '{name}' not found. Available: {list(cls._rules.keys())}")
        return cls._rules[name]
    
    @classmethod
    def list_rules(cls):
        """List all registered rule names."""
        return list(cls._rules.keys())
    
    @classmethod
    def add_rule_dynamically(cls, name: str, evolve_func):
        """
        Dynamically create and register a rule class from a function.
        
        Args:
            name: Name for the new rule
            evolve_func: Function that takes a grid and returns evolved grid
        """
        # Create a new class dynamically
        rule_class = type(
            f"{name.capitalize()}Rule",
            (),
            {'evolve': staticmethod(evolve_func)}
        )
        
        cls._rules[name] = rule_class
        logger.info(f"Dynamically created rule: {name}")
        return rule_class


def memoize_pattern(func):
    """Decorator to cache loaded patterns."""
    cache = {}
    
    @wraps(func)
    def wrapper(filename):
        if filename not in cache:
            cache[filename] = func(filename)
            logger.debug(f"Cached pattern: {filename}")
        else:
            logger.debug(f"Retrieved cached pattern: {filename}")
        return cache[filename]
    
    return wrapper