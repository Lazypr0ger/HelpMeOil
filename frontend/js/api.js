// ===========================
// Конфигурация API
// ===========================
const API_BASE = "http://localhost:8000";

async function apiRequest(url, method = "GET", body = null) {
    const options = { method, headers: {} };

    if (body !== null) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    try {
        const response = await fetch(API_BASE + url, options);
        if (!response.ok) {
            console.error("API error:", response.status, response.statusText);
            return null;
        }
        return await response.json();
    } catch (err) {
        console.error("API fetch error:", err);
        return null;
    }
}


// ===========================
// STATIONS API
// ===========================

// 1. Получить список наших АЗС
async function apiGetOurStations() {
    return await apiRequest("/stations/our");
}

// 2. Получить информацию о конкретной нашей АЗС
async function apiGetOurStation(id) {
    return await apiRequest(`/stations/our/${id}`);
}

// 3. Получить конкурентов по городу
async function apiGetCompetitors(city) {
    return await apiRequest(`/stations/competitors?city=${encodeURIComponent(city)}`);
}


// ===========================
// PRICES API
// ===========================

// 4. История цен станции по топливу
async function apiGetPriceHistory(station_id, fuel, station_type = "competitor") {
    return await apiRequest(
        `/prices/history?station_id=${station_id}&fuel=${fuel}&station_type=${station_type}`
    );
}

// 5. Средние цены по городу
async function apiGetCityAverages(city) {
    return await apiRequest(`/prices/avg?city=${encodeURIComponent(city)}`);
}

// 6. Рекомендованные цены
async function apiGetRecommended(our_station_id) {
    return await apiRequest(`/prices/recommended/${our_station_id}`);
}

// 7. Последние цены станции (быстрый вывод)
async function apiGetLatest(station_id, station_type = "competitor") {
    return await apiRequest(
        `/prices/latest?station_id=${station_id}&station_type=${station_type}`
    );
}


// ===========================
// UPDATE API
// ===========================

// 8. Принудительная загрузка данных
async function apiForceUpdate() {
    return await apiRequest("/update/force", "POST");
}
