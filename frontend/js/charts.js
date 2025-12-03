/* ========================================================
   charts.js — Графики для HelpMeOil (Chart.js + тёмная тема)
   ======================================================== */

/* Глобальные переменные для графиков (чтобы можно было перерисовывать) */
let priceChart = null;
let avgPriceChart = null;


/* ===============================
   Основная загрузка страницы графиков
   =============================== */
document.addEventListener("DOMContentLoaded", () => {
    const select = document.getElementById("fuelSelector");
    if (!select) return;

    // При загрузке — строим графики для выбранного по умолчанию топлива
    loadCharts(select.value);

    // При смене топлива пересобираем графики
    select.addEventListener("change", () => {
        loadCharts(select.value);
    });
});


/* ===============================
   Построение двух графиков
   =============================== */
async function loadCharts(fuelType) {
    const params = new URLSearchParams(window.location.search);
    const stationId = params.get("id");
    if (!stationId) return;

    // Загружаем данные по станции
    const station = await apiGetOurStation(stationId);
    if (!station) return;

    const district = station.district;

    // История цен конкурентов
    const history = await apiGetPriceHistory(station.name, fuelType);

    // Средняя цена по району
    const avgHistory = await prepareDistrictAverages(history);

    drawPriceChart(history, fuelType);
    drawAvgPriceChart(avgHistory, fuelType);
}


/* ===============================
   1. График динамики цен конкурентов
   =============================== */
function drawPriceChart(history, fuelType) {
    const ctx = document.getElementById("priceChart");
    if (!ctx) return;

    // Удаляем старый график, иначе Chart.js наложит новый поверх
    if (priceChart) {
        priceChart.destroy();
    }

    const labels = history.map(item => item.timestamp);
    const values = history.map(item => item.price);

    priceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: `Цена ${fuelType}`,
                data: values,
                borderWidth: 2,
                borderColor: "#4CAF50",
                backgroundColor: "rgba(76, 175, 80, 0.2)",
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: "#e0e0e0" } }
            },
            scales: {
                x: { ticks: { color: "#ccc" }, grid: { color: "#333" } },
                y: { ticks: { color: "#ccc" }, grid: { color: "#333" } }
            }
        }
    });
}


/* ===============================
   2. График средней цены по району
   =============================== */
function drawAvgPriceChart(history, fuelType) {
    const ctx = document.getElementById("avgPriceChart");
    if (!ctx) return;

    if (avgPriceChart) {
        avgPriceChart.destroy();
    }

    const labels = history.map(item => item.timestamp);
    const values = history.map(item => item.avg);

    avgPriceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                label: `Средняя цена ${fuelType} по району`,
                data: values,
                borderWidth: 2,
                borderColor: "#2196F3",
                backgroundColor: "rgba(33, 150, 243, 0.2)",
                tension: 0.3
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { labels: { color: "#e0e0e0" } }
            },
            scales: {
                x: { ticks: { color: "#ccc" }, grid: { color: "#333" } },
                y: { ticks: { color: "#ccc" }, grid: { color: "#333" } }
            }
        }
    });
}


/* ===============================
   Помощник: считаем среднюю цену по району
   =============================== */
async function prepareDistrictAverages(history) {
    // Группируем по timestamp
    const groups = {};

    history.forEach(item => {
        if (!groups[item.timestamp]) {
            groups[item.timestamp] = [];
        }
        groups[item.timestamp].push(item.price);
    });

    const avgArray = [];

    Object.keys(groups).forEach(ts => {
        const prices = groups[ts];
        const avg = prices.reduce((a, b) => a + b, 0) / prices.length;

        avgArray.push({
            timestamp: ts,
            avg: Number(avg.toFixed(2))
        });
    });

    return avgArray;
}
