// OptiFuel Intelligence - Dashboard Logic
const API_URL = "http://localhost:8000";

// Initialize Map
const map = L.map('map', {
    zoomControl: false
}).setView([37.8, -96], 4);

L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: 'OptiFuel Intelligence'
}).addTo(map);

L.control.zoom({ position: 'bottomright' }).addTo(map);

let routeLayer;
let markerGroup = L.layerGroup().addTo(map);

function toggleAdvanced() {
    const el = document.getElementById('advancedConfig');
    el.classList.toggle('hidden');
}

async function calculateRoute() {
    const start = document.getElementById('startNode').value;
    const end = document.getElementById('endNode').value;
    const mpg = document.getElementById('mpg').value;
    const capacity = document.getElementById('capacity').value;
    const btn = document.getElementById('calcBtn');
    const loader = document.getElementById('loader');

    if (!start || !end) {
        alert("Please enter both origin and destination.");
        return;
    }

    // UI States
    loader.classList.remove('hidden');
    btn.disabled = true;

    try {
        const response = await fetch(`${API_URL}/plan_route`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                start: start,
                finish: end,
                mpg: parseFloat(mpg),
                fuel_capacity: parseFloat(capacity),
                reserve_miles: 50
            })
        });

        const data = await response.json();

        if (response.ok) {
            renderResults(data);
        } else {
            alert(data.message || "An error occurred while calculating the route.");
        }
    } catch (error) {
        console.error(error);
        alert("Could not connect to the API. Make sure the backend is running.");
    } finally {
        loader.classList.add('hidden');
        btn.disabled = false;
    }
}

function renderResults(data) {
    document.getElementById('emptyState').classList.add('hidden');
    document.getElementById('results').classList.remove('hidden');

    // Update Stats
    document.getElementById('resDist').innerText = `${data.summary.total_distance_miles} mi`;
    document.getElementById('resCost').innerText = `$${data.summary.total_fuel_cost}`;

    // Clear Map
    if (routeLayer) map.removeLayer(routeLayer);
    markerGroup.clearLayers();

    // Render Route
    const points = polyline.decode(data.route_polyline);
    routeLayer = L.polyline(points, { 
        color: '#3b82f6', 
        weight: 5, 
        opacity: 0.8,
        lineJoin: 'round'
    }).addTo(map);

    map.fitBounds(routeLayer.getBounds(), { padding: [100, 100] });

    // Render Stops
    const stopList = document.getElementById('stopList');
    stopList.innerHTML = '';

    data.fuel_stops.forEach((stop, index) => {
        // Add Marker
        const marker = L.marker([stop.lat, stop.lon], {
            icon: L.divIcon({
                className: 'custom-div-icon',
                html: `<div class="bg-blue-500 w-6 h-6 rounded-full border-2 border-white flex items-center justify-center text-[10px] font-bold text-white shadow-lg">${index + 1}</div>`,
                iconSize: [24, 24],
                iconAnchor: [12, 12]
            })
        }).bindPopup(`
            <div class="text-slate-900 p-2">
                <h4 class="font-bold border-b mb-1">${stop.name}</h4>
                <p class="text-xs">Price: <b>$${stop.price}</b></p>
                <p class="text-[10px] text-gray-500">Stop at mile ${Math.round(stop.dist_from_start)}</p>
            </div>
        `).addTo(markerGroup);

        // Add to List
        const card = document.createElement('div');
        card.className = 'stop-card bg-slate-800 p-3 rounded-xl border border-slate-700 flex items-center gap-4 cursor-pointer hover:border-blue-500 transition';
        card.onclick = () => {
            map.setView([stop.lat, stop.lon], 12);
            marker.openPopup();
        };
        card.innerHTML = `
            <div class="bg-slate-700 w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold text-blue-400">
                ${index + 1}
            </div>
            <div class="flex-1">
                <h4 class="text-sm font-semibold truncate">${stop.name}</h4>
                <p class="text-[10px] text-gray-400">Mile ${Math.round(stop.dist_from_start)} • $${stop.price}/gal</p>
            </div>
            <div class="text-blue-400">
                <i class="fas fa-chevron-right text-xs"></i>
            </div>
        `;
        stopList.appendChild(card);
    });
}
