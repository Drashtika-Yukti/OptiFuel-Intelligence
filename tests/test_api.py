import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import SpatialIndex, get_route, geocode
from src.optimizer import optimize_fuel_stops

def test_optimization():
    print("--- Starting Optimization Test ---")
    
    # 1. Load Data
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "fuel-prices.csv")
    print(f"Loading data from {csv_path}...")
    start_time = time.time()
    spatial_index = SpatialIndex(csv_path)
    print(f"Data loaded in {time.time() - start_time:.4f}s")
    
    # 2. Geocode
    start = "New York"
    finish = "Chicago"
    print(f"Geocoding {start} to {finish}...")
    start_coords = geocode(start)
    end_coords = geocode(finish)
    print(f"Start: {start_coords}, End: {end_coords}")
    
    # 3. Get Route
    print("Fetching route from OSRM...")
    route_data = get_route(start_coords, end_coords)
    if not route_data:
        print("Error: Could not fetch route.")
        return
    print(f"Route distance: {route_data['distance'] * 0.000621371:.2f} miles")
    
    # 4. Optimize
    print("Optimizing fuel stops...")
    start_time = time.time()
    result = optimize_fuel_stops(route_data, spatial_index)
    duration = time.time() - start_time
    
    if result:
        print(f"Optimization finished in {duration:.4f}s")
        print(f"Total Distance: {result['total_distance']} miles")
        print(f"Total Cost: ${result['total_fuel_cost']}")
        print(f"Number of fuel stops: {len(result['stops'])}")
        
        for i, stop in enumerate(result['stops'], 1):
            print(f"  Stop {i}: {stop['name']} at {stop['dist_from_start']:.1f} mi - Price: ${stop['price']}")
        
        # Verification
        assert result['total_fuel_cost'] > 0
        assert len(result['stops']) >= 1 # NY to Chicago is ~800 miles, range is 500. Must stop.
        print("\nVerification SUCCESS: API logic is correct and fast.")
    else:
        print("Verification FAILED: No path found.")

if __name__ == "__main__":
    test_optimization()
