// ==============================
// Получение ID станции из URL
// ==============================
function getStationId() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}


// ==============================
// Загрузка информации о станции
// ==============================
async function loadStation() {
    const stationId = getStationId();

    if (!stationId) {
        alert("ID станции не указан");
        return;
    }

    // Загружаем данные станции
    const station = await apiGetOurStation(stationId);

    if (!station) {
        alert("Станция не найдена");
        return;
    }

    document.getElementById("stationName").textContent = station.name;
    document.getElementById("stationCity").textContent = station.city;
    document.getElementById("stationAddress").textContent = station.address || "—";

    // Ссылка на графики
    document.getElementById("chartLink").href = `charts.html?id=${stationId}`;

    // Загружаем рекомендуемые цены
    loadRecommendedPrices(stationId);

    // Загружаем конкурентов
    loadCompetitors(station.city);
}


// ==============================
// Загрузка рекомендуемых цен
// ==============================
async function loadRecommendedPrices(stationId) {
    const tableBody = document.querySelector("#recommendedTable tbody");
    tableBody.innerHTML = "<tr><td colspan='2'>Загрузка...</td></tr>";

    const data = await apiGetRecommended(stationId);

    if (!data || !data.recommended_prices) {
        tableBody.innerHTML = "<tr><td colspan='2'>Нет данных</td></tr>";
        return;
    }

    tableBody.innerHTML = "";

    Object.entries(data.recommended_prices).forEach(([fuel, price]) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${fuel}</td>
            <td>${price}</td>
        `;
        tableBody.appendChild(tr);
    });
}


// ==============================
// Загрузка конкурентов по городу
// ==============================
async function loadCompetitors(city) {
    const body = document.querySelector("#competitorsTable tbody");
    body.innerHTML = "<tr><td colspan='3'>Загрузка...</td></tr>";

    const competitors = await apiGetCompetitors(city);

    if (!competitors || competitors.length === 0) {
        body.innerHTML = "<tr><td colspan='3'>Нет данных</td></tr>";
        return;
    }

    body.innerHTML = "";

    competitors.forEach(st => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${st.station_name}</td>
            <td>${st.address || "—"}</td>
            <td>${st.brand || "—"}</td>
        `;
        body.appendChild(tr);
    });
}


// ==============================
// Принудительное обновление данных
// ==============================
async function forceUpdateClick() {
    if (!confirm("Обновить данные? Парсер может занять до минуты.")) return;

    const res = await apiForceUpdate();

    if (!res) {
        alert("Ошибка обновления данных");
        return;
    }

    alert("Данные обновлены. Обработано строк: " + res.rows_processed);

    loadStation();
}


// ==============================
// Автозапуск
// ==============================
document.addEventListener("DOMContentLoaded", loadStation);
