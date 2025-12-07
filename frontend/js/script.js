/* ======================================================
   ЛОГИКА ФРОНТЕНДА
   ====================================================== */


/* ==============================================
   1. Загрузка списка НАШИХ станций на index.html
   ============================================== */
async function loadOurStations() {
    const container = document.getElementById("stationsList");
    if (!container) return;

    const stations = await apiGetOurStations();
    if (!stations || stations.length === 0) {
        container.innerHTML = "<p class='text-secondary'>Нет станций</p>";
        return;
    }

    container.innerHTML = "";
    stations.forEach(st => {
        container.innerHTML += `
            <div class="col-md-4 mb-4">
                <div class="card custom-card p-3">
                    <h4 class="text-light">${st.name}</h4>
                    <p class="text-secondary">${st.city}</p>

                    <a href="station.html?id=${st.id}" class="btn btn-success w-100">
                        Открыть
                    </a>
                </div>
            </div>
        `;
    });
}


/* ==============================================
   2. Загрузка данных страницы station.html
   ============================================== */
async function loadStationPage() {
    const title = document.getElementById("stationName");
    if (!title) return;

    const params = new URLSearchParams(window.location.search);
    const id = params.get("id");

    const st = await apiGetOurStation(id);
    if (!st) {
        title.textContent = "Ошибка загрузки";
        return;
    }

    document.getElementById("stationName").textContent = st.name;
    document.getElementById("stationCity").textContent = st.city;

    // Загружаем конкурентов
    loadCompetitors(st.city);

    // Загружаем рекомендованную цену
    loadRecommendedPrice(id);
}


/* ==============================================
   3. Конкуренты в городе
   ============================================== */
async function loadCompetitors(city) {
    const table = document.getElementById("competitorsTable");
    if (!table) return;

    table.innerHTML = `
        <tr><td colspan="7" class="text-center text-secondary">Загрузка...</td></tr>
    `;

    const competitors = await apiGetCompetitorsByCity(city);
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


/* ==============================================
   4. Рекомендованная цена
   ============================================== */
async function loadRecommendedPrice(stationId) {
    const block = document.getElementById("recommendedPrice");
    if (!block) return;

    const res = await apiGetRecommendedPrice(stationId);

    if (!res || res.price === null) {
        block.textContent = "Нет данных";
        block.classList.remove("text-success");
        block.classList.add("text-secondary");
        return;
    }

    block.textContent = res.price + " ₽";
}


/* ==============================================
   5. Автоматический запуск
   ============================================== */
document.addEventListener("DOMContentLoaded", () => {
    loadOurStations();
    loadStationPage();
});
