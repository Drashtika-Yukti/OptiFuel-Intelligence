import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import SpatialIndex, get_route, geocode
from src.optimizer import optimize_fuel_stops

def test_dynamic_profiles():
    print("=== TESTING DYNAMIC VEHICLE PROFILES ===")
    
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "fuel-prices.csv")
    spatial_index = SpatialIndex(csv_path)
    
    start_coords = geocode("New York, NY")
    end_coords = geocode("Chicago, IL") # ~800 miles
    route_data = get_route(start_coords, end_coords)
    
    print("\nScenario 1: Standard Semi-Truck (500mi range, 10 MPG, 50mi reserve)")
    res1 = optimize_fuel_stops(route_data, spatial_index, fuel_capacity=500, mpg=10, reserve_miles=50)
    print(f"Stops: {len(res1['stops'])}, Cost: ${res1['total_fuel_cost']}")
    
    print("\nScenario 2: Low-Range Electric Truck (250mi range, 5 MPG equivalent, 20mi reserve)")
    res2 = optimize_fuel_stops(route_data, spatial_index, fuel_capacity=250, mpg=5, reserve_miles=20)
    print(f"Stops: {len(res2['stops'])}, Cost: ${res2['total_fuel_cost']}")
    
    print("\nScenario 3: Long-Range Tanker (1000mi range, 8 MPG, 100mi reserve)")
    res3 = optimize_fuel_stops(route_data, spatial_index, fuel_capacity=1000, mpg=8, reserve_miles=100)
    print(f"Stops: {len(res3['stops'])}, Cost: ${res3['total_fuel_cost']}")

    # Asserts
    assert len(res2['stops']) > len(res1['stops']), "Low range truck should have more stops"
    assert len(res3['stops']) < len(res1['stops']), "Long range truck should have fewer stops"
    print("\nDYNAMIC PROFILES VERIFIED SUCCESS.")

if __name__ == "__main__":
    test_dynamic_profiles()
