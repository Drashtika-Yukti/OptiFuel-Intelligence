import requests
import json

try:
    r = requests.post('http://localhost:8000/plan_route', json={'start': 'Chicago', 'finish': 'Houston'})
    print(f"Status Code: {r.status_code}")
    data = r.json()
    print(f"Total Fuel Cost: ${data['total_fuel_cost']}")
    print(f"Fuel Stops Found: {len(data['fuel_stops'])}")
    print("Example Stop:", data['fuel_stops'][0]['name'])
    print("API IS WORKING PERFECTLY")
except Exception as e:
    print(f"Error: {e}")
