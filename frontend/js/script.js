console.log("SCRIPT LOADED");
let chartAvg = null;
let chartDyn = null;

document.addEventListener("DOMContentLoaded", () => {
    console.log("SCRIPT STARTED");

    const btn = document.getElementById("forceUpdateBtn");
    if (btn) btn.addEventListener("click", onForceUpdateClick);

    loadStations();
    loadMarketAnalytics();
});



function showLoading() {
    const sOver = document.getElementById("stationsOverlay");
    const sWrap = document.getElementById("stationsWrapper");
    const aOver = document.getElementById("analyticsOverlay");
    const aWrap = document.getElementById("analyticsWrapper");

    if (sOver && sWrap) {
        sOver.style.display = "flex";
        sWrap.classList.add("loading-blur");
    }

    if (aOver && aWrap) {
        aOver.style.display = "flex";
        aWrap.classList.add("loading-blur");
    }
}

function hideLoading() {
    const sOver = document.getElementById("stationsOverlay");
    const sWrap = document.getElementById("stationsWrapper");
    const aOver = document.getElementById("analyticsOverlay");
    const aWrap = document.getElementById("analyticsWrapper");

    if (sOver && sWrap) {
        sOver.style.display = "none";
        sWrap.classList.remove("loading-blur");
    }

    if (aOver && aWrap) {
        aOver.style.display = "none";
        aWrap.classList.remove("loading-blur");
    }
}



async function loadStations() {
    const container = document.getElementById("stationsContainer");
    const counter = document.getElementById("stationsCount");

    container.innerHTML = `<div class="text-secondary">Загрузка станций…</div>`;

    try {
        const data = await getOurStations();

        if (!data.length) {
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

            card.innerHTML = `
                <div class="card-title">${station.name}</div>
                <div class="card-address">${station.city_name || ""} · ${station.address || ""}</div>
            `;

            col.appendChild(card);
            container.appendChild(col);
        });

    } catch (err) {
        console.error(err);
        container.innerHTML = `<div class="text-danger">Ошибка загрузки станций</div>`;
    }
}


async function loadMarketAnalytics() {
    const avgCanvas = document.getElementById("marketAvgChart");
    const dynCanvas = document.getElementById("marketDynamicsChart");
    if (!avgCanvas || !dynCanvas) return;

    try {
        const avgData = await getMarketAverages();
        const historyData = await getMarketHistory();

        const fuels = ["AI92", "AI95", "DIESEL", "GAS"];

        if (chartAvg) chartAvg.destroy();
        if (chartDyn) chartDyn.destroy();


        chartAvg = new Chart(avgCanvas, {
            type: "bar",
            data: {
                labels: fuels,
                datasets: [{
                    label: "Средняя цена, ₽",
                    data: fuels.map(f => avgData[f] ?? null)
                }]
            },
            options: chartOptions
        });

        
        chartDyn = new Chart(dynCanvas, {
            type: "line",
            data: {
                labels: historyData.map(r => r.date),
                datasets: fuels.map((f, i) => ({
                    label: f,
                    data: historyData.map(r => r[f]),
                    borderWidth: 2,
                    fill: false,
                    borderDash: i === 0 ? [] : i === 1 ? [5,5] : i === 2 ? [3,3] : [8,4]
                }))
            },
            options: chartOptions
        });

    } catch (err) {
        console.error("Ошибка аналитики:", err);
    }
}

const chartOptions = {
    plugins: { legend: { labels: { color: "#fff" } } },
    scales: {
        x: { ticks: { color: "#ccc" }, grid: { color: "#333" } },
        y: { ticks: { color: "#ccc" }, grid: { color: "#333" } }
    }
};



async function onForceUpdateClick() {
    const btn = document.getElementById("forceUpdateBtn");
    if (!btn) return;

    btn.disabled = true;
    const old = btn.textContent;
    btn.textContent = "Обновление…";

    showLoading();

    try {
        await forceUpdate();

        btn.textContent = "Обновлено ✓";

        await loadStations();
        await loadMarketAnalytics();

    } catch (e) {
        console.error("Ошибка:", e);
        btn.textContent = "Ошибка ❌";
    }

    hideLoading();

    setTimeout(() => {
        btn.disabled = false;
        btn.textContent = old;
    }, 1500);
}
