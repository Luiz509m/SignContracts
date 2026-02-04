<script>
const API_URL = "https://signcontracts-lastcall.onrender.com/analyze";

async function uploadContract() {
    const fileInput = document.getElementById("fileInput");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");

    if (!fileInput.files.length) {
        alert("Bitte PDF auswählen");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    // UI reset
    loading.style.display = "block";
    result.style.display = "none";

    let response;
    try {
        response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });
    } catch (err) {
        loading.style.display = "none";
        alert("Backend nicht erreichbar. Bitte kurz warten und erneut versuchen.");
        return;
    }

    if (!response.ok) {
        loading.style.display = "none";
        alert("Analyse fehlgeschlagen.");
        return;
    }

    const data = await response.json();

    // ---------- AMPPEL ----------
    const ampel = document.getElementById("ampel");
    ampel.innerText = "AMPEL: " + data.ampel.toUpperCase();
    ampel.className = "ampel " + data.ampel;

    // ---------- ZUSAMMENFASSUNG ----------
    document.getElementById("summary").innerText =
        data.zusammenfassung || "Keine Zusammenfassung verfügbar.";

    // ---------- RISIKEN (checks) ----------
    const risikoList = document.getElementById("risiken");
    risikoList.innerHTML = "";

    if (data.checks) {
        for (const key in data.checks) {
            const check = data.checks[key];
            const li = document.createElement("li");
            li.innerText = `${key.toUpperCase()}: ${check.text}`;
            risikoList.appendChild(li);
        }
    } else {
        const li = document.createElement("li");
        li.innerText = "Keine Risiken erkannt.";
        risikoList.appendChild(li);
    }

    // ---------- EMPFEHLUNGEN ----------
    const empList = document.getElementById("empfehlungen");
    empList.innerHTML = "";

    if (data.empfehlungen && data.empfehlungen.length > 0) {
        data.empfehlungen.forEach(e => {
            const li = document.createElement("li");
            li.innerText = e;
            empList.appendChild(li);
        });
    } else {
        const li = document.createElement("li");
        li.innerText = "Keine Empfehlungen verfügbar.";
        empList.appendChild(li);
    }

    // ---------- EMAIL ----------
    document.getElementById("mail").value =
        data.mail?.text || "Kein Email-Vorschlag vorhanden.";

    // UI anzeigen
    loading.style.display = "none";
    result.style.display = "block";
}
</script>
