"""
Distance calculation utilities using Haversine formula.
"""

import math
from typing import Tuple


class DistanceCalculator:
    """Calculate distances using the Haversine formula."""
    
    EARTH_RADIUS_KM = 6371
    
    @staticmethod
    def haversine(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
        """
        Calculate the great-circle distance between two points on Earth.
        
        Args:
            coord1: Tuple of (latitude, longitude) for first point
            coord2: Tuple of (latitude, longitude) for second point
            
        Returns:
            Distance in kilometers
        """
        lat1, lon1 = coord1
        lat2, lon2 = coord2
        
        # Convert to radians
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)
        
        # Haversine formula
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        
        c = 2 * math.asin(math.sqrt(a))
        
        distance = DistanceCalculator.EARTH_RADIUS_KM * c
        
        return distance
    
    @staticmethod
    def calculate_total_distance(route: list, depot: Tuple[float, float]) -> float:
        """
        Calculate total distance of a route starting and ending at depot.
        
        Args:
            route: List of Delivery objects
            depot: Depot coordinates (latitude, longitude)
            
        Returns:
            Total distance in kilometers
        """
        if not route:
            return 0.0
        
        total = 0.0
        current = depot
        
        for delivery in route:
            distance = DistanceCalculator.haversine(current, delivery.coordinates)
            total += distance
            current = delivery.coordinates
        
        # Return to depot
        total += DistanceCalculator.haversine(current, depot)
        
        return total