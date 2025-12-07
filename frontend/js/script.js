console.log("SCRIPT LOADED");
console.log("SCRIPT STARTED");

document.addEventListener("DOMContentLoaded", () => {
    console.log("DOM READY — calling loadStations()");
    loadStations();
    loadMarketAnalytics();
});

async function loadStations() {
     console.log("loadStations() CALLED");
    const container = document.getElementById("stationsContainer");
    const counter = document.getElementById("stationsCount");

    container.innerHTML = `<div class="text-secondary">Загрузка станций…</div>`;

    try {
        const data = await getOurStations();

        if (!Array.isArray(data) || data.length === 0) {
            container.innerHTML = `<div class="text-warning">Станции не найдены.</div>`;
            counter.textContent = "0 станций";
            return;
        }

        counter.textContent = `Наших АЗС: ${data.length}`;
        container.innerHTML = "";

        data.forEach(station => {
            const col = document.createElement("div");
            col.className = "col-md-4";

            const card = document.createElement("div");
            card.className = "card-station h-100";

            card.addEventListener("click", () => {
                window.location.href = `station.html?id=${station.id}`;
            });

            const title = document.createElement("div");
            title.className = "card-title";
            title.textContent = station.name;

            const subtitle = document.createElement("div");
            subtitle.className = "card-address";
            const city = station.city_name || "";
            const addr = station.address || "";
            subtitle.textContent = city ? `${city}${addr ? " · " + addr : ""}` : addr;


            card.appendChild(title);
            card.appendChild(subtitle);

            col.appendChild(card);
            container.appendChild(col);
        });

    } catch (err) {
        console.error(err);
        container.innerHTML = `<div class="text-danger">Ошибка при загрузке станций</div>`;
        if (counter) counter.textContent = "";
    }
}

async function loadMarketAnalytics() {
    const avgCanvas = document.getElementById("marketAvgChart");
    const dynCanvas = document.getElementById("marketDynamicsChart");

    if (!avgCanvas || !dynCanvas) return;

    try {
        const avgData = await getMarketAverages();
        const historyData = await getMarketHistory();

        /* --------------------------
           1. СРЕДНИЕ ЦЕНЫ (бар-чарт)
        --------------------------- */

        const fuels = ["AI92", "AI95", "DIESEL", "GAS"];
        const avgValues = fuels.map(code => avgData[code] ?? null);

        new Chart(avgCanvas.getContext("2d"), {
            type: "bar",
            data: {
                labels: fuels,
                datasets: [{
                    label: "Средняя цена, ₽",
                    data: avgValues,
                }]
            },
            options: {
                plugins: { legend: { labels: { color: "#fff" } } },
                scales: {
                    x: { ticks: { color: "#ccc" }, grid: { color: "#333" } },
                    y: { ticks: { color: "#ccc" }, grid: { color: "#333" } },
                }
            }
        });

        /* --------------------------------
           2. ДИНАМИКА РЫНКА (line chart)
        -------------------------------- */

        const labels = historyData.map(r => r.date);

        const datasets = fuels.map((fuel, index) => ({
            label: fuel,
            data: historyData.map(r => r[fuel]),
            borderWidth: 2,
            fill: false,
            borderDash: index === 0 ? [] : index === 1 ? [5, 5] : index === 2 ? [3, 3] : [8, 4],
        }));

        new Chart(dynCanvas.getContext("2d"), {
            type: "line",
            data: {
                labels,
                datasets
            },
            options: {
                plugins: { legend: { labels: { color: "#fff" } } },
                scales: {
                    x: { ticks: { color: "#ccc" }, grid: { color: "#333" } },
                    y: { ticks: { color: "#ccc" }, grid: { color: "#333" } },
                }
            }
        });

    } catch (err) {
        console.error("Ошибка аналитики:", err);
    }
}