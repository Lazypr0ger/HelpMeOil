/* ======================================================
   ГЛАВНАЯ ЛОГИКА ФРОНТЕНДА: SCRIPT.JS
   ====================================================== */

/* ===============================
   1. Загрузка списка наших АЗС (index.html)
   =============================== */
async function loadOurStations() {
    const container = document.getElementById("stationsList");
    if (!container) return;

    const stations = await apiGetOurStations();
    if (!stations || stations.length === 0) {
        container.innerHTML = "<p class='text-secondary'>Нет данных</p>";
        return;
    }

    container.innerHTML = "";

    stations.forEach(st => {
        const card = document.createElement("div");
        card.className = "col-md-4 mb-4";

        card.innerHTML = `
            <div class="card custom-card p-3">
                <h4 class="text-light">${st.name}</h4>
                <p class="text-secondary">${st.district}</p>
                <a href="station.html?id=${st.id}" class="btn btn-success w-100">Открыть</a>
            </div>
        `;

        container.appendChild(card);
    });
}


/* ===============================
   2. Загрузка данных выбранной станции (station.html)
   =============================== */
async function loadStationPage() {
    const nameEl = document.getElementById("stationName");
    if (!nameEl) return; // мы не на этой странице

    // Достаём ID из URL
    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");
    if (!id) return;

    const station = await apiGetOurStation(id);
    if (!station) {
        nameEl.textContent = "Ошибка загрузки";
        return;
    }

    // Заполняем данные
    document.getElementById("stationName").textContent = station.name;
    document.getElementById("stationDistrict").textContent = station.district;

    // Загружаем конкурентов
    loadCompetitors(station.district);

    // Загружаем рекомендованную цену
    loadRecommendedPrice(id);
}


/* ===============================
   3. Загрузка конкурентов в таблицу (station.html)
   =============================== */
async function loadCompetitors(district) {
    const table = document.getElementById("competitorsTable");
    if (!table) return;

    table.innerHTML = `
        <tr><td colspan="7" class="text-center text-secondary">Загрузка...</td></tr>
    `;

    const competitors = await apiGetCompetitorsByDistrict(district);

    if (!competitors || competitors.length === 0) {
        table.innerHTML = `
            <tr><td colspan="7" class="text-center text-secondary">Нет данных</td></tr>
        `;
        return;
    }

    table.innerHTML = "";

    competitors.forEach(c => {
        table.innerHTML += `
            <tr>
                <td>${c.station_name}</td>
                <td>${c["Аи-92"] ?? "-"}</td>
                <td>${c["Аи-95"] ?? "-"}</td>
                <td>${c["Аи-95+"] ?? "-"}</td>
                <td>${c["Аи-98"] ?? "-"}</td>
                <td>${c["ДТ"] ?? "-"}</td>
                <td>${c["Газ"] ?? "-"}</td>
            </tr>
        `;
    });
}


/* ===============================
   4. Рекомендуемая цена (station.html)
   =============================== */
async function loadRecommendedPrice(id) {
    const el = document.getElementById("recommendedPrice");
    if (!el) return;

    const result = await apiGetRecommendedPrice(id);

    if (!result || !result.price) {
        el.textContent = "Нет данных";
        el.classList.remove("text-success");
        el.classList.add("text-secondary");
        return;
    }

    el.textContent = result.price + " ₽";
}


/* ===============================
   5. Автоматическое определение страницы
   =============================== */
document.addEventListener("DOMContentLoaded", () => {
    loadOurStations();
    loadStationPage();
});
