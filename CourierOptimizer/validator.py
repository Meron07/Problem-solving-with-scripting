"""
Data validation module using regular expressions and type checks.
"""

import re
from typing import Any
from .exceptions import (
    ValidationError, InvalidCoordinateError,
    InvalidPriorityError, InvalidWeightError
)


class DeliveryValidator:
    """Validates delivery data according to specified rules."""
    
    PRIORITY_PATTERN = r'^(High|Medium|Low)$'
    CUSTOMER_PATTERN = r'^[\w\s\-.,\']+$'
    
    @staticmethod
    def validate_priority(priority: str) -> str:
        """
        Validate priority using regex.
        
        Args:
            priority: Priority string to validate
            
        Returns:
            Validated priority string
            
        Raises:
            InvalidPriorityError: If priority doesn't match pattern
        """
        if not isinstance(priority, str):
            raise InvalidPriorityError(f"Priority must be a string, got {type(priority).__name__}")
        
        if not re.match(DeliveryValidator.PRIORITY_PATTERN, priority):
            raise InvalidPriorityError(
                f"Priority must be 'High', 'Medium', or 'Low', got '{priority}'"
            )
        
        return priority
    
    @staticmethod
    def validate_latitude(lat: Any) -> float:
        """
        Validate latitude value.
        
        Args:
            lat: Latitude value to validate
            
        Returns:
            Validated latitude as float
            
        Raises:
            InvalidCoordinateError: If latitude is invalid
        """
        try:
            lat_float = float(lat)
        except (ValueError, TypeError):
            raise InvalidCoordinateError(f"Latitude must be a number, got '{lat}'")
        
        if not -90 <= lat_float <= 90:
            raise InvalidCoordinateError(
                f"Latitude must be between -90 and 90, got {lat_float}"
            )
        
        return lat_float
    
    @staticmethod
    def validate_longitude(lon: Any) -> float:
        """
        Validate longitude value.
        
        Args:
            lon: Longitude value to validate
            
        Returns:
            Validated longitude as float
            
        Raises:
            InvalidCoordinateError: If longitude is invalid
        """
        try:
            lon_float = float(lon)
        except (ValueError, TypeError):
            raise InvalidCoordinateError(f"Longitude must be a number, got '{lon}'")
        
        if not -180 <= lon_float <= 180:
            raise InvalidCoordinateError(
                f"Longitude must be between -180 and 180, got {lon_float}"
            )
        
        return lon_float
    
    @staticmethod
    def validate_weight(weight: Any) -> float:
        """
        Validate weight value.
        
        Args:
            weight: Weight value to validate
            
        Returns:
            Validated weight as float
            
        Raises:
            InvalidWeightError: If weight is invalid
        """
        try:
            weight_float = float(weight)
        except (ValueError, TypeError):
            raise InvalidWeightError(f"Weight must be a number, got '{weight}'")
        
        if weight_float < 0:
            raise InvalidWeightError(f"Weight must be non-negative, got {weight_float}")
        
        return weight_float
    
    @staticmethod
    def validate_customer_name(name: str) -> str:
        """
        Validate customer name.
        
        Args:
            name: Customer name to validate
            
        Returns:
            Validated customer name
            
        Raises:
            ValidationError: If name is invalid
        """
        if not isinstance(name, str):
            raise ValidationError(f"Customer name must be a string, got {type(name).__name__}")
        
        name = name.strip()
        
        if not name:
            raise ValidationError("Customer name cannot be empty")
        
        if not re.match(DeliveryValidator.CUSTOMER_PATTERN, name):
            raise ValidationError(
                f"Customer name contains invalid characters: '{name}'"
            )
        
        return name