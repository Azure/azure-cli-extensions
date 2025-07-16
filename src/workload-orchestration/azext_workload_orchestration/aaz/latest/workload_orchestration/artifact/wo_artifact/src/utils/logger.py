"""
Logger utility for WO Artifact Generator
"""

import logging
import sys
from typing import Any, Optional

def setup_logger(verbose: bool = False, name: str = "__main__") -> logging.Logger:
    """
    Set up and configure logger instance.
    
    Args:
        verbose: Whether to enable verbose logging
        name: Name for the logger instance
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Configure handler
        handler = logging.StreamHandler(sys.stdout)
        
        # Configure formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        
        # Remove any existing handlers
        logger.handlers.clear()
        
        # Add handler to logger
        logger.addHandler(handler)
        
        # Prevent propagation to root logger
        logger.propagate = False
        
        # Set level based on verbose flag
        logger.setLevel(logging.DEBUG if verbose else logging.INFO)
    
    return logger

class LoggerMixin:
    """
    Mixin class to add logging capabilities to any class.
    """
    
    def __init__(self, verbose: bool = False, *args: Any, **kwargs: Any) -> None:
        """
        Initialize logger mixin.
        
        Args:
            verbose: Whether to enable verbose logging
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
        """
        super().__init__(*args, **kwargs)
        self.logger = setup_logger(verbose=verbose, name=self.__class__.__name__)
