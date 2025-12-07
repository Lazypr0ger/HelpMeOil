/* ======================================================
   API клиент HelpMeOil
   ====================================================== */

const API_BASE = "http://localhost:8000";

async function fetchJSON(url) {
    try {
        const res = await fetch(API_BASE + url);
        if (!res.ok) throw new Error("API error: " + res.status);
        return await res.json();
    } catch (e) {
        console.error("Fetch error:", e);
        return null;
    }
}

/* ================================
   ГОРОДА
   ================================ */
async function apiGetCities() {
    return fetchJSON("/stations/cities");
}

/* ================================
   НАШИ СТАНЦИИ
   ================================ */
async function apiGetOurStations() {
    return fetchJSON("/stations/our");
}

async function apiGetOurStation(id) {
    return fetchJSON(`/stations/our/${id}`);
}

/* ================================
   КОНКУРЕНТЫ ПО ГОРОДУ
   ================================ */
async function apiGetCompetitorsByCity(cityName) {
    return fetchJSON(`/stations/competitors?city=${encodeURIComponent(cityName)}`);
}

/* ================================
   ИСТОРИЯ ЦЕН ПО АЗС
   ================================ */
async function apiGetPriceHistory(stationId, fuelType) {
    return fetchJSON(`/prices/history?station_id=${stationId}&fuel=${encodeURIComponent(fuelType)}`);
}

/* ================================
   РЕКОМЕНДОВАННАЯ ЦЕНА
   ================================ */
async function apiGetRecommendedPrice(stationId) {
    return fetchJSON(`/prices/recommended/${stationId}`);
}
