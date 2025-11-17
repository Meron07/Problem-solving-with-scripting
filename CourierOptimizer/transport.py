"""
Transport mode classes and definitions.
"""

from dataclasses import dataclass
from enum import Enum


@dataclass
class TransportMode:
    """Represents a mode of transportation with its characteristics."""
    
    name: str
    speed_kmh: float
    cost_per_km: float
    co2_per_km: float
    
    def calculate_time(self, distance_km: float) -> float:
        """Calculate time in hours for a given distance."""
        return distance_km / self.speed_kmh if self.speed_kmh > 0 else float('inf')
    
    def calculate_cost(self, distance_km: float) -> float:
        """Calculate cost for a given distance."""
        return distance_km * self.cost_per_km
    
    def calculate_co2(self, distance_km: float) -> float:
        """Calculate CO2 emissions for a given distance."""
        return distance_km * self.co2_per_km
    
    def __str__(self):
        return self.name


class TransportModes:
    """Predefined transport modes."""
    
    CAR = TransportMode("Car", 50, 4, 120)
    BICYCLE = TransportMode("Bicycle", 15, 0, 0)
    WALKING = TransportMode("Walking", 5, 0, 0)
    
    @classmethod
    def get_all(cls):
        """Return all available transport modes."""
        return [cls.CAR, cls.BICYCLE, cls.WALKING]
    
    @classmethod
    def get_by_name(cls, name: str) -> TransportMode:
        """Get transport mode by name."""
        modes = {
            'car': cls.CAR,
            'bicycle': cls.BICYCLE,
            'walking': cls.WALKING
        }
        return modes.get(name.lower())