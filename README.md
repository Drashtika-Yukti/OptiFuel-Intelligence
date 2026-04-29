# Fuel Stop Optimizer API

This API calculates the most cost-effective fuel stops for a vehicle traveling between two locations in the USA.

## Features
- **Optimal Fuel Pricing**: Uses Dijkstra's algorithm to find the sequence of stops that minimizes total cost.
- **High Performance**: Employs a `KDTree` for spatial indexing of fuel stations, ensuring $O(\log N)$ lookup times.
- **Route Integration**: Connects with OpenStreetMap (OSRM) for real-world driving distances.
- **Constraint Aware**: Assumes a 500-mile vehicle range and 10 MPG fuel economy.

## Installation

```bash
pip install -r requirements.txt
```

## Running the API

```bash
# From the project root
python -m src.main
```

## Usage

**Endpoint**: `POST /plan_route`

**Request Body**:
```json
{
  "start": "New York, NY",
  "finish": "Los Angeles, CA"
}
```

**Response**:
- `total_distance_miles`: Total trip length.
- `total_fuel_cost`: Total estimated cost based on cheapest stops.
- `fuel_stops`: List of specific stations to stop at.
- `map_preview_url`: Link to view the route on OpenStreetMap.

## Architecture Decisions for Low Latency
1. **Spatial Indexing**: By using `scipy.spatial.KDTree`, we avoid $O(N)$ scans of the gas station database. We only query stations within a 15-mile radius of sample points along the route.
2. **Graph Pruning**: We sample the route every 50 miles and pick only the top 3 cheapest stations per sample point. This keeps the Dijkstra graph small and solveable in milliseconds.
3. **In-Memory Data**: The CSV is loaded into memory at startup.
