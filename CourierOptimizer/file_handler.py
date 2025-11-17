"""
File I/O operations for reading and writing CSV files.
"""

import csv
import logging
from typing import List, Tuple
from .delivery import Delivery
from .exceptions import ValidationError

logger = logging.getLogger(__name__)


class FileHandler:
    """Handles reading and writing delivery data from/to CSV files."""
    
    @staticmethod
    def read_deliveries(filename: str) -> Tuple[List[Delivery], List[dict]]:
        """
        Read deliveries from CSV file.
        
        Args:
            filename: Path to CSV file
            
        Returns:
            Tuple of (valid deliveries list, rejected rows list)
        """
        deliveries = []
        rejected = []
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                
                for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                    try:
                        delivery = Delivery(
                            customer=row['customer'],
                            latitude=row['latitude'],
                            longitude=row['longitude'],
                            priority=row['priority'],
                            weight_kg=row['weight_kg']
                        )
                        deliveries.append(delivery)
                        
                    except (ValidationError, KeyError, ValueError) as e:
                        logger.warning(f"Row {row_num} rejected: {str(e)}")
                        row['error'] = str(e)
                        row['row_number'] = row_num
                        rejected.append(row)
            
            logger.info(f"Loaded {len(deliveries)} valid deliveries, rejected {len(rejected)} rows")
            
        except FileNotFoundError:
            logger.error(f"File not found: {filename}")
            raise
        except Exception as e:
            logger.error(f"Error reading file {filename}: {str(e)}")
            raise
        
        return deliveries, rejected
    
    @staticmethod
    def write_rejected(filename: str, rejected: List[dict]):
        """
        Write rejected rows to CSV file.
        
        Args:
            filename: Output filename
            rejected: List of rejected row dictionaries
        """
        if not rejected:
            logger.info("No rejected rows to write")
            return
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                fieldnames = list(rejected[0].keys())
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                writer.writeheader()
                writer.writerows(rejected)
            
            logger.info(f"Wrote {len(rejected)} rejected rows to {filename}")
            
        except Exception as e:
            logger.error(f"Error writing rejected file {filename}: {str(e)}")
            raise
    
    @staticmethod
    def write_route(filename: str, route: List[Delivery], depot: Tuple[float, float],
                   mode, metrics: dict):
        """
        Write optimized route to CSV file.
        
        Args:
            filename: Output filename
            route: Ordered list of deliveries
            depot: Depot coordinates
            mode: TransportMode used
            metrics: Dictionary of route metrics
        """
        from .distance import DistanceCalculator
        
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                # Write header
                writer.writerow([
                    'stop_number', 'customer', 'latitude', 'longitude',
                    'priority', 'weight_kg', 'distance_from_prev_km',
                    'cumulative_distance_km', 'eta_hours', 'cost_nok', 'co2_g'
                ])
                
                current_pos = depot
                cumulative_distance = 0.0
                cumulative_time = 0.0
                cumulative_cost = 0.0
                cumulative_co2 = 0.0
                
                for i, delivery in enumerate(route, start=1):
                    distance = DistanceCalculator.haversine(current_pos, delivery.coordinates)
                    cumulative_distance += distance
                    
                    time_for_segment = mode.calculate_time(distance)
                    cost_for_segment = mode.calculate_cost(distance)
                    co2_for_segment = mode.calculate_co2(distance)
                    
                    cumulative_time += time_for_segment
                    cumulative_cost += cost_for_segment
                    cumulative_co2 += co2_for_segment
                    
                    writer.writerow([
                        i,
                        delivery.customer,
                        delivery.latitude,
                        delivery.longitude,
                        delivery.priority,
                        delivery.weight_kg,
                        f"{distance:.3f}",
                        f"{cumulative_distance:.3f}",
                        f"{cumulative_time:.3f}",
                        f"{cumulative_cost:.2f}",
                        f"{cumulative_co2:.2f}"
                    ])
                    
                    current_pos = delivery.coordinates
                
                # Return to depot
                distance_to_depot = DistanceCalculator.haversine(current_pos, depot)
                cumulative_distance += distance_to_depot
                cumulative_time += mode.calculate_time(distance_to_depot)
                cumulative_cost += mode.calculate_cost(distance_to_depot)
                cumulative_co2 += mode.calculate_co2(distance_to_depot)
                
                writer.writerow([
                    len(route) + 1,
                    'DEPOT (Return)',
                    depot[0],
                    depot[1],
                    'N/A',
                    0,
                    f"{distance_to_depot:.3f}",
                    f"{cumulative_distance:.3f}",
                    f"{cumulative_time:.3f}",
                    f"{cumulative_cost:.2f}",
                    f"{cumulative_co2:.2f}"
                ])
            
            logger.info(f"Wrote route to {filename}")
            
        except Exception as e:
            logger.error(f"Error writing route file {filename}: {str(e)}")
            raise
    
    @staticmethod
    def write_metrics(filename: str, metrics: dict, mode, objective: str):
        """
        Write optimization metrics to CSV file.
        
        Args:
            filename: Output filename
            metrics: Dictionary of metrics
            mode: TransportMode used
            objective: Optimization objective
        """
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                
                writer.writerow(['Metric', 'Value', 'Unit'])
                writer.writerow(['Transport Mode', mode.name, ''])
                writer.writerow(['Optimization Objective', objective.capitalize(), ''])
                writer.writerow(['Total Distance', f"{metrics['total_distance_km']:.3f}", 'km'])
                writer.writerow(['Total Time', f"{metrics['total_time_hours']:.3f}", 'hours'])
                writer.writerow(['Total Cost', f"{metrics['total_cost_nok']:.2f}", 'NOK'])
                writer.writerow(['Total CO2', f"{metrics['total_co2_g']:.2f}", 'g'])
            
            logger.info(f"Wrote metrics to {filename}")
            
        except Exception as e:
            logger.error(f"Error writing metrics file {filename}: {str(e)}")
            raise