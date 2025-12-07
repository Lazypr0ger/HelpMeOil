// ==========================
// Загрузка списка наших станций
// ==========================

document.addEventListener("DOMContentLoaded", () => {
    loadStations();
});

async function loadStations() {
    const stationsTable = document.getElementById("stationsTableBody");
    stationsTable.innerHTML = "<tr><td colspan='4'>Загрузка...</td></tr>";

    const stations = await apiGetOurStations();

    if (!stations || stations.length === 0) {
        stationsTable.innerHTML = "<tr><td colspan='4'>Нет данных</td></tr>";
        return;
    }

    stationsTable.innerHTML = "";

    stations.forEach(st => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td>${st.name}</td>
            <td>${st.address ?? "—"}</td>
            <td>${st.city}</td>
            <td>
                <a href="station.html?id=${st.id}" class="btn btn-primary btn-sm">Перейти</a>
            </td>
        `;

        stationsTable.appendChild(tr);
    });
}


// ==========================
// Принудительное обновление данных
// ==========================

async function forceUpdateClick() {
    if (!confirm("Обновить данные принудительно? Это может занять до 30–60 секунд.")) return;

    const res = await apiForceUpdate();

    if (!res) {
        alert("Ошибка обновления!");
        return;
    }

    alert("Данные обновлены. Обработано строк: " + res.rows_processed);

    // перезагружаем таблицу
    loadStations();
}
