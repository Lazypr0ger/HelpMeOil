// frontend/station.js

document.addEventListener("DOMContentLoaded", async () => {
    const stationId = getStationIdFromUrl();
    if (!stationId) {
        alert("Не указан id станции в URL");
        return;
    }

    await loadStation(stationId);
    await loadCompetitors(stationId);
    await loadPriceHistory(stationId);
    await loadRecommended(stationId);        // ← добавлено
    await loadRecommendedHistory(stationId); // ← добавлено
    await loadCityAvg(stationId);            // ← добавлено (если будет плашка)
});

function getStationIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}

/* ---------------------------------------------------
   1. ЗАГРУЗКА ОСНОВНЫХ ДАННЫХ АЗС
--------------------------------------------------- */
async function loadStation(id) {
    const nameEl = document.getElementById("stationName");
    const addrEl = document.getElementById("stationAddress");

    try {
        const data = await getStationDetails(id);

        nameEl.textContent = data.name || "АЗС";
        addrEl.textContent = `${data.city_name || ""} · ${data.address || ""}`;

    } catch (err) {
        console.error("Ошибка загрузки станции:", err);
        nameEl.textContent = "Ошибка загрузки станции";
    }
}

/* ---------------------------------------------------
   2. РЕКОМЕНДУЕМЫЕ ЦЕНЫ
--------------------------------------------------- */
async function loadRecommended(id) {
    const container = document.getElementById("recommendedPrices");
    container.innerHTML = `<div class="text-secondary">Загрузка…</div>`;

    try {
        const rec = await apiGet(`/our-stations/${id}/recommended`);
        container.innerHTML = "";

        const fuels = ["AI92", "AI95", "DIESEL", "GAS"];

        fuels.forEach(code => {
            if (rec[code] != null) {
                const col = document.createElement("div");
                col.className = "col-md-3";

                col.innerHTML = `
                    <div class="card-station">
                        <div class="card-title">${code}</div>
                        <div class="mt-2">${rec[code].toFixed(2)} ₽</div>
                    </div>
                `;
                container.appendChild(col);
            }
        });

    } catch (err) {
        console.error("Ошибка рекомендованных цен:", err);
        container.innerHTML = `<div class="text-danger">Не удалось загрузить данные</div>`;
    }
}

/* ---------------------------------------------------
   3. КОНКУРЕНТЫ
--------------------------------------------------- */
async function loadCompetitors(id) {
    const tbody = document.querySelector("#competitorsTable tbody");
    tbody.innerHTML = `<tr><td colspan="5" class="text-secondary">Загрузка…</td></tr>`;

    try {
        const data = await getStationCompetitors(id);

        if (!data.length) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-warning">Нет конкурентов</td></tr>`;
            return;
        }

        tbody.innerHTML = "";

        data.forEach(row => {
            const tr = document.createElement("tr");
            const fuels = ["AI92", "AI95", "DIESEL", "GAS"];

            tr.innerHTML = `<td>${row.station_name}</td>` +
                fuels.map(code => `<td>${row.prices?.[code] ? row.prices[code].toFixed(2) : "—"}</td>`).join("");

            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error("Ошибка конкурентов:", err);
        tbody.innerHTML = `<tr><td colspan="5" class="text-danger">Ошибка загрузки</td></tr>`;
    }
}

/* ---------------------------------------------------
   4. ИСТОРИЯ ЦЕН НАШЕЙ АЗС
--------------------------------------------------- */
async function loadPriceHistory(id) {
    const canvas = document.getElementById("priceHistoryChart");
    if (!canvas) return;

    try {
        const data = await getStationPriceHistory(id);
        if (!data.length) return;

        const labels = data.map(d => d.date);
        const fuels = ["AI92", "AI95", "DIESEL", "GAS"];

        const datasets = fuels.map((code, idx) => ({
            label: code,
            data: data.map(d => d[code]),
            borderWidth: 2,
            fill: false,
            borderDash: idx === 0 ? [] : idx === 1 ? [5, 5] : idx === 2 ? [3, 3] : [8, 4]
        }));

        new Chart(canvas.getContext("2d"), {
            type: "line",
            data: { labels, datasets },
            options: {
                plugins: { legend: { labels: { color: "#fff" } } },
                scales: {
                    x: { ticks: { color: "#ccc" }, grid: { color: "#333" } },
                    y: { ticks: { color: "#ccc" }, grid: { color: "#333" } }
                }
            }
        });

    } catch (err) {
        console.error("Ошибка истории цен:", err);
    }
}

/* ---------------------------------------------------
   5. РЕКОМЕНДУЕМЫЕ ЦЕНЫ — ИСТОРИЯ
--------------------------------------------------- */
async function loadRecommendedHistory(id) {
    const data = await apiGet(`/our-stations/${id}/recommended/history`);
    console.log("История рекомендованных:", data);
}

/* ---------------------------------------------------
   6. СРЕДНЯЯ ЦЕНА ПО ГОРОДУ
--------------------------------------------------- */
async function loadCityAvg(id) {
    const avg = await apiGet(`/our-stations/${id}/city-avg`);
    console.log("Средние по городу:", avg);
}
