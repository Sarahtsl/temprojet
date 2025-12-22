console.log("dashboard.js chargé");

async function loadLatest() {
    try {
        const res = await fetch("/latest/");
        const data = await res.json();

        console.log("Dernière mesure:", data);

        const tempEl = document.getElementById("tempValue");
        const humEl = document.getElementById("humValue");
        const tempTimeEl = document.getElementById("tempTime");
        const humTimeEl = document.getElementById("humTime");

        const temp = data.temp;
        const hum = data.hum;
        const dateStr = data.date;

        if (typeof temp === "number") {
            tempEl.textContent = temp.toFixed(1);
        } else {
            tempEl.textContent = "--";
        }

        if (typeof hum === "number") {
            humEl.textContent = hum.toFixed(1);
        } else {
            humEl.textContent = "--";
        }

        if (dateStr) {
            const date = new Date(dateStr);
            if (!isNaN(date.getTime())) {
                const diffSec = Math.round((Date.now() - date.getTime()) / 1000);
                const msg =
                    "il y a : " + diffSec + " secondes (" + date.toLocaleTimeString() + ")";
                tempTimeEl.textContent = msg;
                humTimeEl.textContent = msg;
            } else {
                tempTimeEl.textContent = "Date invalide";
                humTimeEl.textContent = "Date invalide";
            }
        } else {
            tempTimeEl.textContent = "Aucune mesure pour le moment";
            humTimeEl.textContent = "Aucune mesure pour le moment";
        }
    } catch (e) {
        console.error("Erreur API /latest/ :", e);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    loadLatest();
    setInterval(loadLatest, 5000);
});
