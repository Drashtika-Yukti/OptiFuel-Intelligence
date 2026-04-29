from fastapi.testclient import TestClient
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_invalid_route():
    # Test with non-existent cities to verify error handling
    response = client.post("/plan_route", json={
        "start": "InvalidCity123",
        "finish": "UnknownPlace456"
    })
    # Our professional error handler returns 400 for GeocodingError
    assert response.status_code == 400
    assert "error" in response.json()

def test_successful_route():
    # Test a standard route
    response = client.post("/plan_route", json={
        "start": "New York, NY",
        "finish": "Chicago, IL",
        "mpg": 10,
        "fuel_capacity": 500
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "total_fuel_cost" in data["summary"]
    assert len(data["fuel_stops"]) >= 1
