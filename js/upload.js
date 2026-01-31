const API_URL = "https://signcontracts-lastcall.onrender.com/analyze";

async function uploadContract() {
    const fileInput = document.getElementById("fileInput");
    const file = fileInput.files[0];

    if (!file) {
        alert("Bitte PDF auswählen");
        return;
    }

    const formData = new FormData();
    formData.append("file", file);

    document.getElementById("result").style.display = "none";

    const response = await fetch(API_URL, {
        method: "POST",
        body: formData
    });

    if (!response.ok) {
        alert("Analyse fehlgeschlagen");
        return;
    }

    const data = await response.json();

    document.getElementById("result").style.display = "block";
    document.getElementById("ampel").innerText = data.ampel.toUpperCase();

    const r = document.getElementById("risiken");
    r.innerHTML = "";
    data.top_risiken.forEach(x => {
        const li = document.createElement("li");
        li.innerText = x.beschreibung;
        r.appendChild(li);
    });

    const e = document.getElementById("empfehlungen");
    e.innerHTML = "";
    data.empfehlungen.forEach(x => {
        const li = document.createElement("li");
        li.innerText = x;
        e.appendChild(li);
    });

    document.getElementById("mail").value = data.mail.text;
}
