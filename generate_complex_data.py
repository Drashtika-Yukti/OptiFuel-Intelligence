import csv
import random

# Generating 10,000 mock gas stations across the USA
stations = []
for i in range(10000):
    lat = round(random.uniform(24.0, 49.0), 4)
    lon = round(random.uniform(-125.0, -67.0), 4)
    price = round(random.uniform(3.00, 5.00), 2) # Wider price range
    name = f"Mega_Stop_{i}"
    address = f"{random.randint(100, 9999)} Highway Blvd"
    city = f"City_{random.randint(1, 500)}"
    state = random.choice(["NY", "CA", "TX", "FL", "IL", "PA", "OH", "GA", "NC", "MI"])
    stations.append([name, address, city, state, lat, lon, price])

with open('f:/Templates/fuel_stop_optimizer/data/fuel-prices.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['Truckstop Name', 'Address', 'City', 'State', 'lat', 'lon', 'Retail Price'])
    writer.writerows(stations)

print("Generated 10,000 gas stations for stress testing.")
