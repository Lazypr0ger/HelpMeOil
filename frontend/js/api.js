// frontend/api.js
console.log("SCRIPT LOADED");

// Базовый адрес бэкенда
const API_BASE = "http://localhost:8000";

// Универсальный GET
async function apiGet(path) {
    const res = await fetch(API_BASE + path);
    if (!res.ok) {
        console.error(`GET ${path} failed: ${res.status}`);
        return null;
    }
    return res.json();
}

// Универсальный POST
async function apiPost(path) {
    const res = await fetch(API_BASE + path, { method: "POST" });
    if (!res.ok) {
        console.error(`POST ${path} failed: ${res.status}`);
        return null;
    }
    return res.json().catch(() => ({}));
}

/* -----------------------------------------------------
   НАШИ АЗС (frontend ←→ backend /our-stations API)
----------------------------------------------------- */

// Получить список всех наших виртуальных АЗС
async function getOurStations() {
    return apiGet("/our-stations");
}

// Получить информацию по одной нашей АЗС
async function getStationDetails(id) {
    return apiGet(`/our-stations/${id}`);
}

// Получить конкурентов в этом городе
async function getStationCompetitors(id) {
    return apiGet(`/our-stations/${id}/competitors`);
}

// История цен по нашей АЗС
async function getStationPriceHistory(id) {
    return apiGet(`/our-stations/${id}/history`);
}

/* -----------------------------------------------------
   ОБНОВЛЕНИЕ ДАННЫХ
----------------------------------------------------- */

// Принудительно запустить парсер
async function forceUpdate() {
    return apiPost("/update/force");
}
