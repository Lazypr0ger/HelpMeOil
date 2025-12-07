// frontend/station.js

document.addEventListener("DOMContentLoaded", () => {
    const stationId = getStationIdFromUrl();
    if (!stationId) {
        alert("Не указан id станции в URL");
        return;
    }

    loadStation(stationId);
    loadCompetitors(stationId);
    loadPriceHistory(stationId);
});

function getStationIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}

// Загрузка основных данных АЗС
async function loadStation(id) {
    const nameEl = document.getElementById("stationName");
    const addrEl = document.getElementById("stationAddress");
    const recContainer = document.getElementById("recommendedPrices");

    try {
        const data = await getStationDetails(id);
        // Ожидаемый формат:
        // {
        //   id, name, address, city_name,
        //   recommended_prices: { AI92, AI95, DIESEL, GAS }
        // }

        nameEl.textContent = data.name || "АЗС";
        addrEl.textContent = `${data.city_name || ""} · ${data.address || ""}`;

        recContainer.innerHTML = "";
        const rec = data.recommended_prices || {};
        const fuels = ["AI92", "AI95", "DIESEL", "GAS"];

        fuels.forEach(code => {
            if (rec[code] != null) {
                const col = document.createElement("div");
                col.className = "col-md-3";

                const card = document.createElement("div");
                card.className = "card-station";

                const title = document.createElement("div");
                title.className = "card-title";
                title.textContent = code;

                const price = document.createElement("div");
                price.className = "mt-2";
                price.textContent = `${rec[code].toFixed(2)} ₽`;

                card.appendChild(title);
                card.appendChild(price);
                col.appendChild(card);
                recContainer.appendChild(col);
            }
        });

    } catch (err) {
        console.error(err);
        nameEl.textContent = "Ошибка загрузки станции";
        addrEl.textContent = "";
    }
}

// Загрузка таблицы конкурентов
async function loadCompetitors(id) {
    const tbody = document.querySelector("#competitorsTable tbody");
    tbody.innerHTML = `<tr><td colspan="5" class="text-secondary">Загрузка…</td></tr>`;

    try {
        const data = await getStationCompetitors(id);
        // Ожидаемый формат:
        // [{ station_name, prices: { AI92, AI95, DIESEL, GAS } }, ...]

        if (!Array.isArray(data) || data.length === 0) {
            tbody.innerHTML = `<tr><td colspan="5" class="text-warning">Конкуренты не найдены.</td></tr>`;
            return;
        }

        tbody.innerHTML = "";

        data.forEach(row => {
            const tr = document.createElement("tr");

            const nameTd = document.createElement("td");
            nameTd.textContent = row.station_name;
            tr.appendChild(nameTd);

            const fuels = ["AI92", "AI95", "DIESEL", "GAS"];
            fuels.forEach(code => {
                const td = document.createElement("td");
                const price = row.prices?.[code];
                td.textContent = price != null ? price.toFixed(2) : "—";
                tr.appendChild(td);
            });

            tbody.appendChild(tr);
        });

    } catch (err) {
        console.error(err);
        tbody.innerHTML = `<tr><td colspan="5" class="text-danger">Ошибка загрузки конкурентов</td></tr>`;
    }
}

// График истории цен нашей АЗС
async function loadPriceHistory(id) {
    const canvas = document.getElementById("priceHistoryChart");
    if (!canvas) return;

    try {
        const data = await getStationPriceHistory(id);
        // Ожидаемый формат:
        // [{ date: "2025-12-01", AI92: ..., AI95: ..., DIESEL: ..., GAS: ... }, ...]

        if (!Array.isArray(data) || data.length === 0) {
            return;
        }

        const labels = data.map(d => d.date);
        const fuels = ["AI92", "AI95", "DIESEL", "GAS"];

        const datasets = fuels.map((code, idx) => ({
            label: code,
            data: data.map(d => d[code]),
            borderWidth: 2,
            fill: false,
            borderDash: idx === 0 ? [] : idx === 1 ? [5, 5] : idx === 2 ? [2, 3] : [8, 4]
        }));

        new Chart(canvas.getContext("2d"), {
            type: "line",
            data: {
                labels,
                datasets
            },
            options: {
                plugins: {
                    legend: { labels: { color: "#ffffff" } }
                },
                scales: {
                    x: {
                        ticks: { color: "#cccccc" },
                        grid: { color: "#333333" }
                    },
                    y: {
                        ticks: { color: "#cccccc" },
                        grid: { color: "#333333" }
                    }
                }
            }
        });

    } catch (err) {
        console.error("Ошибка истории цен:", err);
    }
}
