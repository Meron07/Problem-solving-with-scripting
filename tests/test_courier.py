"""
Test suite for CourierOptimizer package.
"""

import pytest
import os
from CourierOptimizer.delivery import Delivery
from CourierOptimizer.validator import DeliveryValidator
from CourierOptimizer.transport import TransportModes
from CourierOptimizer.distance import DistanceCalculator
from CourierOptimizer.optimizer import CourierOptimizer
from CourierOptimizer.exceptions import (
    ValidationError, InvalidCoordinateError,
    InvalidPriorityError, InvalidWeightError, EmptyDataError
)


class TestDeliveryValidator:
    """Test validation functions."""
    
    def test_validate_priority_valid(self):
        """Test valid priority values."""
        assert DeliveryValidator.validate_priority('High') == 'High'
        assert DeliveryValidator.validate_priority('Medium') == 'Medium'
        assert DeliveryValidator.validate_priority('Low') == 'Low'
    
    def test_validate_priority_invalid(self):
        """Test invalid priority values."""
        with pytest.raises(InvalidPriorityError):
            DeliveryValidator.validate_priority('VeryHigh')
        
        with pytest.raises(InvalidPriorityError):
            DeliveryValidator.validate_priority('high')  # Case sensitive
    
    def test_validate_latitude_valid(self):
        """Test valid latitude values."""
        assert DeliveryValidator.validate_latitude(0) == 0
        assert DeliveryValidator.validate_latitude(59.9139) == 59.9139
        assert DeliveryValidator.validate_latitude(-90) == -90
        assert DeliveryValidator.validate_latitude(90) == 90
    
    def test_validate_latitude_invalid(self):
        """Test invalid latitude values."""
        with pytest.raises(InvalidCoordinateError):
            DeliveryValidator.validate_latitude(91)
        
        with pytest.raises(InvalidCoordinateError):
            DeliveryValidator.validate_latitude(-91)
        
        with pytest.raises(InvalidCoordinateError):
            DeliveryValidator.validate_latitude('invalid')
    
    def test_validate_longitude_valid(self):
        """Test valid longitude values."""
        assert DeliveryValidator.validate_longitude(0) == 0
        assert DeliveryValidator.validate_longitude(10.7522) == 10.7522
        assert DeliveryValidator.validate_longitude(-180) == -180
        assert DeliveryValidator.validate_longitude(180) == 180
    
    def test_validate_longitude_invalid(self):
        """Test invalid longitude values."""
        with pytest.raises(InvalidCoordinateError):
            DeliveryValidator.validate_longitude(181)
        
        with pytest.raises(InvalidCoordinateError):
            DeliveryValidator.validate_longitude(-181)
    
    def test_validate_weight_valid(self):
        """Test valid weight values."""
        assert DeliveryValidator.validate_weight(0) == 0
        assert DeliveryValidator.validate_weight(5.5) == 5.5
        assert DeliveryValidator.validate_weight(100) == 100
    
    def test_validate_weight_invalid(self):
        """Test invalid weight values."""
        with pytest.raises(InvalidWeightError):
            DeliveryValidator.validate_weight(-1)
        
        with pytest.raises(InvalidWeightError):
            DeliveryValidator.validate_weight('invalid')
    
    def test_validate_customer_name_valid(self):
        """Test valid customer names."""
        assert DeliveryValidator.validate_customer_name('John Doe') == 'John Doe'
        assert DeliveryValidator.validate_customer_name("O'Brien") == "O'Brien"
    
    def test_validate_customer_name_invalid(self):
        """Test invalid customer names."""
        with pytest.raises(ValidationError):
            DeliveryValidator.validate_customer_name('')
        
        with pytest.raises(ValidationError):
            DeliveryValidator.validate_customer_name('   ')


class TestDelivery:
    """Test Delivery class."""
    
    def test_delivery_creation_valid(self):
        """Test creating valid delivery."""
        delivery = Delivery(
            customer='John Doe',
            latitude=59.9139,
            longitude=10.7522,
            priority='High',
            weight_kg=5.0
        )
        
        assert delivery.customer == 'John Doe'
        assert delivery.latitude == 59.9139
        assert delivery.longitude == 10.7522
        assert delivery.priority == 'High'
        assert delivery.weight_kg == 5.0
    
    def test_delivery_priority_weight(self):
        """Test priority weight calculation."""
        high = Delivery('Customer', 60, 10, 'High', 5)
        medium = Delivery('Customer', 60, 10, 'Medium', 5)
        low = Delivery('Customer', 60, 10, 'Low', 5)
        
        assert high.priority_weight == 0.6
        assert medium.priority_weight == 1.0
        assert low.priority_weight == 1.2
    
    def test_delivery_coordinates(self):
        """Test coordinates property."""
        delivery = Delivery('Customer', 59.9139, 10.7522, 'High', 5)
        assert delivery.coordinates == (59.9139, 10.7522)


class TestDistanceCalculator:
    """Test distance calculation."""
    
    def test_haversine_same_point(self):
        """Test distance between same point."""
        coord = (59.9139, 10.7522)
        distance = DistanceCalculator.haversine(coord, coord)
        assert distance == 0
    
    def test_haversine_known_distance(self):
        """Test distance between Oslo and Bergen (approximately 300km)."""
        oslo = (59.9139, 10.7522)
        bergen = (60.3913, 5.3221)
        distance = DistanceCalculator.haversine(oslo, bergen)
        
        # Should be roughly 300km
        assert 250 < distance < 350
    
    def test_calculate_total_distance(self):
        """Test total route distance calculation."""
        depot = (59.9139, 10.7522)
        deliveries = [
            Delivery('A', 60.0, 11.0, 'High', 5),
            Delivery('B', 60.5, 11.5, 'Medium', 3)
        ]
        
        total = DistanceCalculator.calculate_total_distance(deliveries, depot)
        assert total > 0


class TestTransportModes:
    """Test transport mode calculations."""
    
    def test_car_calculations(self):
        """Test car mode calculations."""
        car = TransportModes.CAR
        
        assert car.calculate_time(50) == 1.0  # 50km at 50km/h = 1 hour
        assert car.calculate_cost(10) == 40  # 10km at 4 NOK/km
        assert car.calculate_co2(10) == 1200  # 10km at 120 g/km
    
    def test_bicycle_calculations(self):
        """Test bicycle mode calculations."""
        bicycle = TransportModes.BICYCLE
        
        assert bicycle.calculate_time(15) == 1.0
        assert bicycle.calculate_cost(100) == 0
        assert bicycle.calculate_co2(100) == 0
    
    def test_get_by_name(self):
        """Test getting mode by name."""
        assert TransportModes.get_by_name('car') == TransportModes.CAR
        assert TransportModes.get_by_name('bicycle') == TransportModes.BICYCLE
        assert TransportModes.get_by_name('walking') == TransportModes.WALKING


class TestCourierOptimizer:
    """Test optimizer functionality."""
    
    def test_optimizer_creation(self):
        """Test creating optimizer."""
        depot = (59.9139, 10.7522)
        optimizer = CourierOptimizer(depot)
        assert optimizer.depot == depot
    
    def test_optimize_empty_deliveries(self):
        """Test optimization with empty delivery list."""
        depot = (59.9139, 10.7522)
        optimizer = CourierOptimizer(depot)
        
        with pytest.raises(EmptyDataError):
            optimizer.optimize([], TransportModes.CAR, 'time')
    
    def test_optimize_single_delivery(self):
        """Test optimization with single delivery."""
        depot = (59.9139, 10.7522)
        optimizer = CourierOptimizer(depot)
        
        deliveries = [
            Delivery('Customer A', 60.0, 11.0, 'High', 5)
        ]
        
        result = optimizer.optimize(deliveries, TransportModes.CAR, 'time')
        assert len(result) == 1
        assert result[0].customer == 'Customer A'
    
    def test_optimize_multiple_deliveries(self):
        """Test optimization with multiple deliveries."""
        depot = (59.9139, 10.7522)
        optimizer = CourierOptimizer(depot)
        
        deliveries = [
            Delivery('A', 60.0, 11.0, 'High', 5),
            Delivery('B', 60.1, 11.1, 'Medium', 3),
            Delivery('C', 59.95, 10.8, 'Low', 2)
        ]
        
        result = optimizer.optimize(deliveries, TransportModes.CAR, 'time')
        assert len(result) == 3
    
    def test_calculate_route_metrics(self):
        """Test route metrics calculation."""
        depot = (59.9139, 10.7522)
        optimizer = CourierOptimizer(depot)
        
        route = [
            Delivery('A', 60.0, 11.0, 'High', 5)
        ]
        
        metrics = optimizer.calculate_route_metrics(route, TransportModes.CAR)
        
        assert 'total_distance_km' in metrics
        assert 'total_time_hours' in metrics
        assert 'total_cost_nok' in metrics
        assert 'total_co2_g' in metrics
        assert all(v >= 0 for v in metrics.values())


if __name__ == '__main__':
    pytest.main([__file__, '-v'])