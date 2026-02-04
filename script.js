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

    loading.style.display = "block";
    result.style.display = "none";

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Backend-Fehler");
        }

        const data = await response.json();

        // Ampel
        const ampel = document.getElementById("ampel");
        ampel.innerText = "AMPEL: " + data.ampel.toUpperCase();
        ampel.className = "ampel " + data.ampel;

        // Summary
        document.getElementById("summary").innerText =
            data.zusammenfassung || "Keine Zusammenfassung vorhanden.";

        // Risiken
        const risiken = document.getElementById("risiken");
        risiken.innerHTML = "";
        data.top_risiken.forEach(r => {
            const li = document.createElement("li");
            li.innerText = r.beschreibung;
            risiken.appendChild(li);
        });

        // Empfehlungen
        const empfehlungen = document.getElementById("empfehlungen");
        empfehlungen.innerHTML = "";
        data.empfehlungen.forEach(e => {
            const li = document.createElement("li");
            li.innerText = e;
            empfehlungen.appendChild(li);
        });

        // Mail
        document.getElementById("mail").value = data.mail?.text || "";

        loading.style.display = "none";
        result.style.display = "block";

    } catch (err) {
        loading.style.display = "none";
        alert("Analyse fehlgeschlagen – Backend erreichbar?");
        console.error(err);
    }
}
