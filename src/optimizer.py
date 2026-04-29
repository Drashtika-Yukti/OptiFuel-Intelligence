import heapq
from .utils import haversine, SpatialIndex
import polyline

def optimize_fuel_stops(route_data, spatial_index, fuel_capacity=500, mpg=10, reserve_miles=50):
    """
    Finds optimal fuel stops along a route with dynamic vehicle profiles.
    """
    points = polyline.decode(route_data['geometry'])
    total_dist = route_data['distance'] * 0.000621371  # Convert meters to miles
    
    # 1. Sample the route to find candidate stations
    # We take a point every ~50 miles to search for stations
    candidates = []
    accumulated_dist = 0
    last_pt = points[0]
    
    # Add start as a candidate
    candidates.append({
        'name': 'START',
        'lat': points[0][0],
        'lon': points[0][1],
        'price': 0,
        'dist_from_start': 0
    })

    # Sample the path
    step_size = 50 # miles
    target_dist = step_size
    
    for pt in points[1:]:
        d = haversine(last_pt[0], last_pt[1], pt[0], pt[1])
        accumulated_dist += d
        last_pt = pt
        
        if accumulated_dist >= target_dist:
            # Find nearby stations
            stations = spatial_index.find_nearby_stations(pt[0], pt[1], radius_miles=15)
            # Pick top 3 cheapest at this point to keep graph small
            stations.sort(key=lambda x: x['Retail Price'])
            for s in stations[:3]:
                s['dist_from_start'] = accumulated_dist
                candidates.append({
                    'name': s['Truckstop Name'],
                    'lat': s['lat'],
                    'lon': s['lon'],
                    'price': s['Retail Price'],
                    'dist_from_start': accumulated_dist
                })
            target_dist += step_size

    # Add finish as a candidate
    candidates.append({
        'name': 'FINISH',
        'lat': points[-1][0],
        'lon': points[-1][1],
        'price': 0,
        'dist_from_start': total_dist
    })

    # 2. Build adjacency list for Dijkstra
    # Each node can reach any node further down the route if within (fuel_capacity - reserve_miles)
    effective_range = fuel_capacity - reserve_miles
    
    adj = [[] for _ in range(len(candidates))]
    for i in range(len(candidates)):
        for j in range(i + 1, len(candidates)):
            # Distance along the route check
            route_dist = candidates[j]['dist_from_start'] - candidates[i]['dist_from_start']
            
            if route_dist <= effective_range:
                gallons = route_dist / mpg
                cost = gallons * candidates[i]['price']
                adj[i].append((j, cost))
            else:
                if route_dist > fuel_capacity: # Hard limit
                     break

    # 3. Run Dijkstra
    N = len(candidates)
    min_costs = [float('inf')] * N
    prev = [-1] * N
    min_costs[0] = 0
    
    pq = [(0, 0)] # (cost, index)
    
    while pq:
        curr_cost, u = heapq.heappop(pq)
        
        if curr_cost > min_costs[u]:
            continue
            
        for v, weight in adj[u]:
            if min_costs[u] + weight < min_costs[v]:
                min_costs[v] = min_costs[u] + weight
                prev[v] = u
                heapq.heappush(pq, (min_costs[v], v))
    
    # Reconstruct path
    path = []
    curr = N - 1
    if min_costs[curr] == float('inf'):
        return None # No path found
        
    while curr != -1:
        path.append(candidates[curr])
        curr = prev[curr]
    path.reverse()
    
    return {
        "stops": path[1:-1], # Remove START and FINISH
        "total_fuel_cost": round(min_costs[N-1], 2),
        "total_distance": round(total_dist, 2)
    }
