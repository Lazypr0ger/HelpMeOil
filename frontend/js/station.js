
console.log("STATION JS LOADED");
let chartHistory = null;

document.addEventListener("DOMContentLoaded", async () => {
    const id = getId();
    if (!id) return alert("ID станции не указан");

    await loadStation(id);
    await loadRecommended(id);
    await loadCompetitors(id);
    await loadPriceHistory(id);
    await loadRecommendedHistory(id);
    await loadCityAvg(id);
});

function getId() {
    return new URLSearchParams(location.search).get("id");
}


async function loadStation(id) {
    const name = document.getElementById("stationName");
    const addr = document.getElementById("stationAddress");

    try {
        const data = await getStationDetails(id);
        name.textContent = data.name;
        addr.textContent = `${data.city_name} · ${data.address}`;
    } catch (e) {
        console.error(e);
        name.textContent = "Ошибка загрузки";
    }
}


async function loadRecommended(id) {
    const box = document.getElementById("recommendedPrices");
    box.innerHTML = "<div class='text-secondary'>Загрузка…</div>";

    try {
        const rec = await apiGet(`/our-stations/${id}/recommended`);
        box.innerHTML = "";

        ["AI92","AI95","DIESEL","GAS"].forEach(f => {
            if (rec[f] != null) {
                box.innerHTML += `
                <div class="col-md-3">
                    <div class="card-station">
                        <div class="card-title">${f}</div>
                        <div class="mt-2">${rec[f].toFixed(2)} ₽</div>
                    </div>
                </div>`;
            }
        });
    } catch (e) {
        console.error("Ошибка рекомендованных:", e);
    }
}



async function loadCompetitors(id) {
    const tbody = document.querySelector("#competitorsTable tbody");
    tbody.innerHTML = `<tr><td colspan="5" class="text-secondary">Загрузка…</td></tr>`;

    try {
        const comps = await getStationCompetitors(id);
        tbody.innerHTML = "";

        const fuels = ["AI92","AI95","DIESEL","GAS"];

        comps.forEach(c => {
            tbody.innerHTML += `
            <tr>
                <td>${c.station_name}</td>
                ${fuels.map(f => `<td>${c.prices[f]?.toFixed?.(2) ?? "—"}</td>`).join("")}
            </tr>`;
        });
    } catch (e) {
        console.error("Ошибка конкурентов:", e);
    }
}


async function loadPriceHistory(id) {
    const canvas = document.getElementById("priceHistoryChart");
    if (!canvas) return;

    try {
        const data = await getStationPriceHistory(id);
        if (!data.length) return;

        const fuels = ["AI92", "AI95", "DIESEL", "GAS"];


        if (chartHistory) chartHistory.destroy();

        chartHistory = new Chart(canvas, {
            type: "line",
            data: {
                labels: data.map(d => d.date),
                datasets: fuels.map((code, idx) => ({
                    label: code,
                    data: data.map(d => d[code]),
                    borderWidth: 2,
                    fill: false,
                    borderDash: idx === 0 ? [] : idx === 1 ? [5,5] : idx === 2 ? [3,3] : [8,4]
                }))
            },
            options: {
                plugins: { 
                    legend: { labels: { color: "#fff" } }
                },
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



async function loadRecommendedHistory(id) {
    console.log("recommended history:", await apiGet(`/our-stations/${id}/recommended/history`));
}

async function loadCityAvg(id){
    console.log("city avg:", await apiGet(`/our-stations/${id}/city-avg`));
}
