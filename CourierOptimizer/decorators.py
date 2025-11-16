"""
Metaprogramming decorators for CourierOptimizer.
Includes timing, logging, and validation decorators.
"""

import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def timing_decorator(func):
    """Decorator to measure and log execution time of functions."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        logger.info(f"Starting {func.__name__} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start_time))}")
        
        try:
            result = func(*args, **kwargs)
            end_time = time.time()
            elapsed_time = end_time - start_time
            
            logger.info(f"Completed {func.__name__} in {elapsed_time:.4f} seconds")
            logger.info(f"End time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
            
            return result
        except Exception as e:
            end_time = time.time()
            elapsed_time = end_time - start_time
            logger.error(f"Failed {func.__name__} after {elapsed_time:.4f} seconds: {str(e)}")
            raise
    
    return wrapper


def validate_inputs(func):
    """Decorator to validate function inputs."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.debug(f"Validating inputs for {func.__name__}")
        return func(*args, **kwargs)
    
    return wrapper


def error_handler(default_return=None):
    """Decorator to handle errors gracefully and return a default value."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {str(e)}")
                if default_return is not None:
                    return default_return
                raise
        return wrapper
    return decorator