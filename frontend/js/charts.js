
function getStationId() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}


document.addEventListener("DOMContentLoaded", async () => {
    const id = getStationId();
    if (!id) {
        alert("Не указан id станции");
        return;
    }

    await loadStationInfo(id);
    await loadCharts(id);
});


async function loadStationInfo(id) {
    const station = await apiGetOurStation(id);

    if (!station) {
        alert("Станция не найдена");
        return;
    }

    document.getElementById("stationName").innerText = station.name;
    document.getElementById("stationCity").innerText = station.city;
    document.getElementById("stationAddress").innerText = station.address || "—";
}


async function loadCharts(id) {
    const fuels = ["AI92", "AI95", "DIESEL", "GAS"];

    for (let fuel of fuels) {
        await buildChart(id, fuel);
    }
}



async function buildChart(stationId, fuel) {
    const ctx = document.getElementById(`chart${fuel}`);

    // 1. История цен нашей станции
    const myHistory = await apiGetPriceHistory(stationId, fuel, "our");

    // 2. Город станции
    const station = await apiGetOurStation(stationId);
    const city = station.city;

    // 3. Средние цены конкурентов
    const cityAvg = await apiGetCityAverages(city);

    // Фильтр по виду топлива
    const avgFuel = cityAvg.filter(p => p.fuel_type_id && p.fuel_type_id !== null);

  

    const myData = myHistory.map(r => ({
        x: r.date,
        y: r.price
    }));

    const avgData = cityAvg
        .filter(r => r.fuel_type_id === fuelTypeId(fuel))
        .map(r => ({
            x: r.date,
            y: r.avg
        }));



    new Chart(ctx, {
        type: "line",
        data: {
            datasets: [
                {
                    label: "Наша АЗС",
                    data: myData,
                    borderColor: "#0275d8",
                    tension: 0.2
                },
                {
                    label: "Средняя цена конкурентов",
                    data: avgData,
                    borderColor: "#d9534f",
                    tension: 0.2
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                x: { type: "time", time: { unit: "day" } },
                y: { beginAtZero: false }
            }
        }
    });
}



function fuelTypeId(code) {
    switch (code) {
        case "AI92": return 1;
        case "AI95": return 2;
        case "DIESEL": return 3;
        case "GAS": return 4;
        default: return null;
    }
}
