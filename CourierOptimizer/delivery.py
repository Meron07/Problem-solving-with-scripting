"""
Delivery class representing a single delivery point.
"""

from dataclasses import dataclass
from typing import Tuple
from .validator import DeliveryValidator


@dataclass
class Delivery:
    """Represents a delivery with customer info and location."""
    
    customer: str
    latitude: float
    longitude: float
    priority: str
    weight_kg: float
    
    def __post_init__(self):
        """Validate all fields after initialization."""
        self.customer = DeliveryValidator.validate_customer_name(self.customer)
        self.latitude = DeliveryValidator.validate_latitude(self.latitude)
        self.longitude = DeliveryValidator.validate_longitude(self.longitude)
        self.priority = DeliveryValidator.validate_priority(self.priority)
        self.weight_kg = DeliveryValidator.validate_weight(self.weight_kg)
    
    @property
    def coordinates(self) -> Tuple[float, float]:
        """Return coordinates as a tuple (latitude, longitude)."""
        return (self.latitude, self.longitude)
    
    @property
    def priority_weight(self) -> float:
        """
        Return priority multiplier for optimization.
        High = 0.6, Medium = 1.0, Low = 1.2
        """
        priority_weights = {
            'High': 0.6,
            'Medium': 1.0,
            'Low': 1.2
        }
        return priority_weights[self.priority]
    
    def __str__(self):
        return f"{self.customer} ({self.priority}, {self.weight_kg}kg)"