/* ======================================================
   API клиент для HelpMeOil
   Универсальный модуль для общения с backend
   ====================================================== */

const API_BASE = "http://localhost:8000"; 
// позже заменим на env-переменную или production URL


/* ===============================
   Запрос наших АЗС HelpMeOil
   =============================== */
async function apiGetOurStations() {
    return fetchJSON("/stations/our");
}


/* ===============================
   Запрос данных по конкретной нашей АЗС
   =============================== */
async function apiGetOurStation(id) {
    return fetchJSON(`/stations/our/${id}`);
}


/* ===============================
   Конкуренты по району
   =============================== */
async function apiGetCompetitorsByDistrict(district) {
    return fetchJSON(`/stations/competitors?district=${encodeURIComponent(district)}`);
}


/* ===============================
   История цен (временной ряд)
   =============================== */
async function apiGetPriceHistory(stationName, fuelType) {
    return fetchJSON(`/prices/history?station=${encodeURIComponent(stationName)}&fuel=${encodeURIComponent(fuelType)}`);
}


/* ===============================
   Рекомендуемая цена
   =============================== */
async function apiGetRecommendedPrice(stationId) {
    return fetchJSON(`/analytics/recommended/${stationId}`);
}


/* ===============================
   Базовая функция FETCH
   =============================== */
async function fetchJSON(endpoint) {
    try {
        const response = await fetch(API_BASE + endpoint);

        if (!response.ok) {
            throw new Error(`Ошибка API: ${response.status}`);
        }

        return await response.json();

    } catch (error) {
        console.error("API error:", error);
        return null;
    }
}
