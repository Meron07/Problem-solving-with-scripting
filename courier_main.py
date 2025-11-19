"""
Main CLI interface for CourierOptimizer.
"""

import sys
import logging
from typing import Tuple
from CourierOptimizer.optimizer import CourierOptimizer
from CourierOptimizer.transport import TransportModes
from CourierOptimizer.file_handler import FileHandler
from CourierOptimizer.exceptions import CourierOptimizerError, EmptyDataError


def setup_logging():
    """Configure logging to both file and console."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('run.log'),
            logging.StreamHandler()
        ]
    )


def get_depot_coordinates() -> Tuple[float, float]:
    """Prompt user for depot coordinates."""
    print("\n=== Depot Location ===")
    while True:
        try:
            lat = float(input("Enter depot latitude (e.g., 59.9139 for Oslo): "))
            lon = float(input("Enter depot longitude (e.g., 10.7522 for Oslo): "))
            
            if not (-90 <= lat <= 90):
                print("Latitude must be between -90 and 90")
                continue
            if not (-180 <= lon <= 180):
                print("Longitude must be between -180 and 180")
                continue
            
            return (lat, lon)
        except ValueError:
            print("Please enter valid numbers")


def select_transport_mode():
    """Display menu and get transport mode selection."""
    print("\n=== Transport Mode ===")
    print("1. Car (50 km/h, 4 NOK/km, 120 g CO2/km)")
    print("2. Bicycle (15 km/h, 0 NOK/km, 0 g CO2/km)")
    print("3. Walking (5 km/h, 0 NOK/km, 0 g CO2/km)")
    
    while True:
        choice = input("\nSelect transport mode (1-3): ").strip()
        
        if choice == '1':
            return TransportModes.CAR
        elif choice == '2':
            return TransportModes.BICYCLE
        elif choice == '3':
            return TransportModes.WALKING
        else:
            print("Invalid choice. Please enter 1, 2, or 3")


def select_optimization_objective():
    """Display menu and get optimization objective."""
    print("\n=== Optimization Objective ===")
    print("1. Fastest total time")
    print("2. Lowest total cost")
    print("3. Lowest CO2 emissions")
    
    while True:
        choice = input("\nSelect optimization objective (1-3): ").strip()
        
        if choice == '1':
            return 'time'
        elif choice == '2':
            return 'cost'
        elif choice == '3':
            return 'co2'
        else:
            print("Invalid choice. Please enter 1, 2, or 3")


def display_summary(metrics: dict, mode, objective: str, num_deliveries: int):
    """Display formatted summary of optimization results."""
    print("\n" + "=" * 60)
    print("OPTIMIZATION SUMMARY".center(60))
    print("=" * 60)
    print(f"\nTransport Mode: {mode.name}")
    print(f"Optimization Objective: {objective.capitalize()}")
    print(f"Number of Deliveries: {num_deliveries}")
    print("\n--- Route Metrics ---")
    print(f"Total Distance: {metrics['total_distance_km']:.2f} km")
    print(f"Total Time: {metrics['total_time_hours']:.2f} hours ({metrics['total_time_hours']*60:.0f} minutes)")
    print(f"Total Cost: {metrics['total_cost_nok']:.2f} NOK")
    print(f"Total CO2 Emissions: {metrics['total_co2_g']:.2f} g ({metrics['total_co2_g']/1000:.3f} kg)")
    print("\n--- Output Files ---")
    print("• route.csv - Detailed route with all stops")
    print("• metrics.csv - Summary metrics")
    print("• rejected.csv - Invalid input rows (if any)")
    print("• run.log - Execution log")
    print("=" * 60)


def main():
    """Main entry point for CourierOptimizer CLI."""
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print("=" * 60)
    print("NORDIC EXPRESS - COURIER ROUTE OPTIMIZER".center(60))
    print("=" * 60)
    
    try:
        # Get input file
        input_file = input("\nEnter deliveries CSV file path (default: deliveries.csv): ").strip()
        if not input_file:
            input_file = "deliveries.csv"
        
        # Read deliveries
        logger.info(f"Reading deliveries from {input_file}")
        deliveries, rejected = FileHandler.read_deliveries(input_file)
        
        if not deliveries:
            raise EmptyDataError("No valid deliveries found in input file")
        
        # Write rejected rows if any
        if rejected:
            FileHandler.write_rejected("rejected.csv", rejected)
            print(f"\nWarning: {len(rejected)} invalid rows written to rejected.csv")
        
        # Get depot location
        depot = get_depot_coordinates()
        
        # Get transport mode
        mode = select_transport_mode()
        
        # Get optimization objective
        objective = select_optimization_objective()
        
        # Create optimizer and optimize
        print(f"\nOptimizing route for {len(deliveries)} deliveries...")
        optimizer = CourierOptimizer(depot)
        optimized_route = optimizer.optimize(deliveries, mode, objective)
        
        # Calculate metrics
        metrics = optimizer.calculate_route_metrics(optimized_route, mode)
        
        # Write output files
        FileHandler.write_route("route.csv", optimized_route, depot, mode, metrics)
        FileHandler.write_metrics("metrics.csv", metrics, mode, objective)
        
        # Display summary
        display_summary(metrics, mode, objective, len(deliveries))
        
        logger.info("Optimization completed successfully")
        print("\nOptimization completed successfully!")
        
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        print(f"\nError: File not found - {e}")
        sys.exit(1)
    
    except EmptyDataError as e:
        logger.error(str(e))
        print(f"\nError: {e}")
        sys.exit(1)
    
    except CourierOptimizerError as e:
        logger.error(f"Optimization error: {e}")
        print(f"\nError: {e}")
        sys.exit(1)
    
    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    
    except Exception as e:
        logger.exception("Unexpected error occurred")
        print(f"\nUnexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()