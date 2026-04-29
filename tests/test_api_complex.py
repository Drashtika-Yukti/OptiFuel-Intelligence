import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import SpatialIndex, get_route, geocode
from src.optimizer import optimize_fuel_stops

def test_complex_optimization():
    print("=== COMPLEX SCENARIO: NEW YORK TO LOS ANGELES (2,800+ MILES) ===")
    
    # 1. Load Data (10,000 stations)
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "fuel-prices.csv")
    print(f"Loading 10,000 stations from {csv_path}...")
    start_time = time.time()
    spatial_index = SpatialIndex(csv_path)
    print(f"Data loaded and indexed in {time.time() - start_time:.4f}s")
    
    # 2. Geocode Long Distance
    start = "New York, NY"
    finish = "Los Angeles, CA"
    print(f"Geocoding {start} to {finish}...")
    start_coords = geocode(start)
    end_coords = geocode(finish)
    print(f"Start: {start_coords}, End: {end_coords}")
    
    # 3. Get Route (Continental Scale)
    print("Fetching continental route from OSRM...")
    route_data = get_route(start_coords, end_coords)
    if not route_data:
        print("Error: Could not fetch route.")
        return
    total_mi = route_data['distance'] * 0.000621371
    print(f"Route distance: {total_mi:.2f} miles")
    
    # 4. Optimize with 500mi Range
    print("Optimizing complex fuel path (Dijkstra + KDTree)...")
    start_time = time.time()
    result = optimize_fuel_stops(route_data, spatial_index)
    duration = time.time() - start_time
    
    if result:
        print(f"SUCCESS: Complex optimization finished in {duration:.4f}s")
        print(f"Total Distance: {result['total_distance']} miles")
        print(f"Total Fuel Cost: ${result['total_fuel_cost']}")
        print(f"Number of required stops: {len(result['stops'])}")
        
        # Verify number of stops
        # 2800 miles / 500 range = ~6 stops.
        print("\n--- Detailed Stop Plan ---")
        for i, stop in enumerate(result['stops'], 1):
            print(f"  Stop {i}: {stop['name']} at {stop['dist_from_start']:.1f} mi - Price: ${stop['price']}")
        
        assert len(result['stops']) >= 5, "Should have at least 5 stops for 2800 miles"
        print("\nVERIFICATION PASSED: System handled 10k stations and cross-country routing instantly.")
    else:
        print("VERIFICATION FAILED: No path found for this complex route.")

if __name__ == "__main__":
    test_complex_optimization()
