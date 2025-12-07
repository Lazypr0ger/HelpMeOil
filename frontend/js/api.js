console.log("API LOADED");

// Backend URL
const API_BASE = "http://localhost:8000";

// GET
async function apiGet(path) {
    const res = await fetch(API_BASE + path);
    if (!res.ok) {
        console.error(`GET ${path} failed: ${res.status}`);
        return null;
    }
    return res.json();
}

// POST
async function apiPost(path) {
    const res = await fetch(API_BASE + path, { method: "POST" });
    if (!res.ok) {
        console.error(`POST ${path} failed: ${res.status}`);
        return null;
    }
    return res.json().catch(() => ({}));
}

// OUR STATIONS API
async function getOurStations() {
    return apiGet("/our-stations");
}

async function getStationDetails(id) {
    return apiGet(`/our-stations/${id}`);
}

async function getStationCompetitors(id) {
    return apiGet(`/our-stations/${id}/competitors`);
}

async function getStationPriceHistory(id) {
    return apiGet(`/our-stations/${id}/history`);
}

// MARKET API
async function getMarketAverages() {
    return apiGet("/analytics/market/avg");
}

async function getMarketHistory() {
    return apiGet("/analytics/market/history");
}

// UPDATE API
async function forceUpdate() {
    return apiPost("/update/force");
}
