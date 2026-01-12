const API_URL = "https://signcontracts-lastcall.onrender.com/analyse";

async function uploadContract() {
    const fileInput = document.getElementById("fileInput");
    if (!fileInput.files.length) {
        alert("Bitte PDF auswählen");
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    document.getElementById("loading").classList.remove("hidden");
    document.getElementById("result").classList.add("hidden");

    let response;
    try {
        response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });
    } catch (error) {
        alert("Server nicht erreichbar. Bitte 20–30 Sekunden warten und erneut versuchen.");
        document.getElementById("loading").classList.add("hidden");
        return;
    }

    if (!response.ok) {
        alert("Fehler bei der Analyse. Bitte erneut versuchen.");
        document.getElementById("loading").classList.add("hidden");
        return;
    }

    const data = await response.json();

    document.getElementById("loading").classList.add("hidden");
    document.getElementById("result").classList.remove("hidden");

    // Ampel
    const ampel = document.getElementById("ampel");
    ampel.textContent = data.ampel.toUpperCase();
    ampel.className = "ampel " + data.ampel;

    // Risiken
    const risikoList = document.getElementById("risiken");
    risikoList.innerHTML = "";
    data.top_risiken.forEach(r => {
        const li = document.createElement("li");
        li.textContent = r.beschreibung;
        risikoList.appendChild(li);
    });

    // Empfehlungen
    const empList = document.getElementById("empfehlungen");
    empList.innerHTML = "";
    data.empfehlungen.forEach(e => {
        const li = document.createElement("li");
        li.textContent = e;
        empList.appendChild(li);
    });

    // Mail
    document.getElementById("mail").value = data.mail.text;
}
