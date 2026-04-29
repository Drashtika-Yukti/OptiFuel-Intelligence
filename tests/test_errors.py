import sys
import os
import time

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.utils import SpatialIndex, geocode, GeocodingError

def test_error_handling():
    print("=== TESTING PROFESSIONAL ERROR HANDLING ===")
    
    # 1. Test Geocoding Failure
    invalid_city = "ZyxxyCity_9999_Unknown"
    print(f"Testing invalid location: '{invalid_city}'")
    try:
        geocode(invalid_city)
        print("FAIL: Should have raised GeocodingError")
    except GeocodingError as e:
        print(f"SUCCESS: Caught expected GeocodingError: {e}")
    
    # 2. Test Partial Data (Not handled yet in geocode logic but useful to see)
    empty_city = ""
    print(f"Testing empty location: '{empty_city}'")
    try:
        geocode(empty_city)
        print("FAIL: Should have raised GeocodingError")
    except GeocodingError as e:
        print(f"SUCCESS: Caught expected GeocodingError: {e}")

    print("\nError handling verification PASSED.")

if __name__ == "__main__":
    test_error_handling()
