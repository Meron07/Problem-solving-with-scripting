"""
Main optimization engine for courier routing.
"""

import logging
from typing import List, Tuple, Callable
from itertools import permutations
from .delivery import Delivery
from .transport import TransportMode
from .distance import DistanceCalculator
from .decorators import timing_decorator
from .exceptions import EmptyDataError, OptimizationError

logger = logging.getLogger(__name__)


class CourierOptimizer:
    """Optimizes delivery routes based on various criteria."""
    
    def __init__(self, depot: Tuple[float, float]):
        """
        Initialize optimizer with depot location.
        
        Args:
            depot: Depot coordinates (latitude, longitude)
        """
        self.depot = depot
        self.distance_calc = DistanceCalculator()
    
    @timing_decorator
    def optimize(self, deliveries: List[Delivery], mode: TransportMode,
                 objective: str = 'time') -> List[Delivery]:
        """
        Optimize delivery route based on selected objective.
        
        Args:
            deliveries: List of Delivery objects
            mode: TransportMode to use
            objective: One of 'time', 'cost', or 'co2'
            
        Returns:
            Optimized list of deliveries
            
        Raises:
            EmptyDataError: If deliveries list is empty
            OptimizationError: If optimization fails
        """
        if not deliveries:
            raise EmptyDataError("No deliveries to optimize")
        
        logger.info(f"Optimizing {len(deliveries)} deliveries using {mode.name} for {objective}")
        
        # For small number of deliveries, use brute force
        if len(deliveries) <= 10:
            return self._brute_force_optimize(deliveries, mode, objective)
        else:
            # For larger sets, use greedy nearest neighbor
            return self._greedy_optimize(deliveries, mode, objective)
    
    def _brute_force_optimize(self, deliveries: List[Delivery],
                              mode: TransportMode, objective: str) -> List[Delivery]:
        """
        Brute force optimization by trying all permutations.
        
        Args:
            deliveries: List of Delivery objects
            mode: TransportMode to use
            objective: Optimization objective
            
        Returns:
            Best route found
        """
        objective_func = self._get_objective_function(mode, objective)
        
        best_route = None
        best_score = float('inf')
        
        total_perms = 0
        for perm in permutations(deliveries):
            total_perms += 1
            route = list(perm)
            score = objective_func(route)
            
            if score < best_score:
                best_score = score
                best_route = route
        
        logger.info(f"Evaluated {total_perms} permutations, best score: {best_score:.2f}")
        
        return best_route
    
    def _greedy_optimize(self, deliveries: List[Delivery],
                        mode: TransportMode, objective: str) -> List[Delivery]:
        """
        Greedy nearest neighbor optimization.
        
        Args:
            deliveries: List of Delivery objects
            mode: TransportMode to use
            objective: Optimization objective
            
        Returns:
            Optimized route
        """
        route = []
        remaining = deliveries.copy()
        current_pos = self.depot
        
        while remaining:
            # Find best next delivery
            best_delivery = None
            best_score = float('inf')
            
            for delivery in remaining:
                distance = self.distance_calc.haversine(current_pos, delivery.coordinates)
                
                # Apply priority weight
                score = distance * delivery.priority_weight
                
                # Adjust score based on objective
                if objective == 'time':
                    score = mode.calculate_time(score)
                elif objective == 'cost':
                    score = mode.calculate_cost(score)
                elif objective == 'co2':
                    score = mode.calculate_co2(score)
                
                if score < best_score:
                    best_score = score
                    best_delivery = delivery
            
            route.append(best_delivery)
            remaining.remove(best_delivery)
            current_pos = best_delivery.coordinates
        
        logger.info(f"Greedy optimization completed")
        
        return route
    
    def _get_objective_function(self, mode: TransportMode,
                                objective: str) -> Callable[[List[Delivery]], float]:
        """
        Get objective function for route evaluation.
        
        Args:
            mode: TransportMode to use
            objective: Optimization objective
            
        Returns:
            Function that takes a route and returns a score
        """
        def evaluate_route(route: List[Delivery]) -> float:
            total_distance = 0.0
            current = self.depot
            position_multiplier = 1.0
            
            for i, delivery in enumerate(route):
                distance = self.distance_calc.haversine(current, delivery.coordinates)
                
                # Apply priority weight based on position in route
                weighted_distance = distance * delivery.priority_weight * position_multiplier
                total_distance += weighted_distance
                
                current = delivery.coordinates
                position_multiplier += 0.1  # Slight penalty for later deliveries
            
            # Return to depot
            total_distance += self.distance_calc.haversine(current, self.depot)
            
            # Calculate final score based on objective
            if objective == 'time':
                return mode.calculate_time(total_distance)
            elif objective == 'cost':
                return mode.calculate_cost(total_distance)
            elif objective == 'co2':
                return mode.calculate_co2(total_distance)
            else:
                return total_distance
        
        return evaluate_route
    
    def calculate_route_metrics(self, route: List[Delivery],
                               mode: TransportMode) -> dict:
        """
        Calculate all metrics for a route.
        
        Args:
            route: List of deliveries in order
            mode: TransportMode used
            
        Returns:
            Dictionary with total_distance, total_time, total_cost, total_co2
        """
        total_distance = self.distance_calc.calculate_total_distance(route, self.depot)
        
        return {
            'total_distance_km': total_distance,
            'total_time_hours': mode.calculate_time(total_distance),
            'total_cost_nok': mode.calculate_cost(total_distance),
            'total_co2_g': mode.calculate_co2(total_distance)
        }