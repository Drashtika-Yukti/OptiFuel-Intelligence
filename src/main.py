from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from .utils import SpatialIndex, get_route, geocode, logger, FuelOptimizerError, GeocodingError, RoutingError
from .optimizer import optimize_fuel_stops
import os
import time

app = FastAPI(
    title="OptiFuel Intelligence API",
    description="Strategic fuel stop optimization for enterprise logistics."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize spatial index
CSV_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "fuel-prices.csv")
try:
    spatial_index = SpatialIndex(CSV_PATH)
    logger.info(f"Database loaded successfully with {len(spatial_index.df)} stations.")
except Exception as e:
    logger.critical(f"Failed to load station database: {e}")
    # We don't exit here, but the API will fail gracefully on requests

class RouteRequest(BaseModel):
    start: str = Field(..., example="New York, NY")
    finish: str = Field(..., example="Los Angeles, CA")
    mpg: float = Field(default=10.0, gt=0, description="Miles per gallon")
    fuel_capacity: float = Field(default=500.0, gt=0, description="Maximum range in miles")
    reserve_miles: float = Field(default=50.0, ge=0, description="Safety buffer in miles")

# --- Professional Error Handlers ---

@app.exception_handler(FuelOptimizerError)
async def fuel_optimizer_exception_handler(request: Request, exc: FuelOptimizerError):
    logger.warning(f"Business Logic Error: {exc}")
    status_code = 400
    if isinstance(exc, RoutingError):
        status_code = 502 # Bad Gateway for external service failure
    
    return JSONResponse(
        status_code=status_code,
        content={"error": exc.__class__.__name__, "message": str(exc)},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"UNEXPECTED ERROR: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "InternalServerError", "message": "An unexpected error occurred. Our team has been notified."},
    )

# --- Routes ---

@app.post("/plan_route")
async def plan_route(request: RouteRequest):
    start_time = time.time()
    logger.info(f"New Route Request: {request.start} -> {request.finish}")
    
    # 1. Geocode locations (Raises GeocodingError if fails)
    start_coords = geocode(request.start)
    end_coords = geocode(request.finish)
    
    # 2. Get route from OSRM (Raises RoutingError if fails)
    route_data = get_route(start_coords, end_coords)
    
    # 3. Optimize fuel stops
    result = optimize_fuel_stops(
        route_data, 
        spatial_index, 
        fuel_capacity=request.fuel_capacity, 
        mpg=request.mpg, 
        reserve_miles=request.reserve_miles
    )
    
    if not result:
        logger.error(f"No fuel path found for {request.start} to {request.finish}")
        raise FuelOptimizerError("Could not find a valid refueling path. The destination might be unreachable within the vehicle range.")
    
    duration = time.time() - start_time
    logger.info(f"Optimization complete for {request.start} -> {request.finish} in {duration:.2f}s. Cost: ${result['total_fuel_cost']}")
    
    # 4. Format response
    map_url = f"https://www.openstreetmap.org/directions?engine=fossgis_osrm_car&route={start_coords[0]}%2C{start_coords[1]}%3B{end_coords[0]}%2C{end_coords[1]}"
    
    return {
        "status": "success",
        "request": {"start": request.start, "finish": request.finish},
        "summary": {
            "total_distance_miles": result["total_distance"],
            "total_fuel_cost": result["total_fuel_cost"],
            "fuel_stops_count": len(result["stops"]),
            "processing_time_sec": round(duration, 3)
        },
        "fuel_stops": result["stops"],
        "route_polyline": route_data['geometry'],
        "map_preview_url": map_url
    }

@app.get("/health")
def health():
    return {
        "status": "healthy", 
        "stations_loaded": len(spatial_index.df),
        "timestamp": time.time()
    }
