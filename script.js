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

    const response = await fetch("http://127.0.0.1:8000/analyze", {
        method: "POST",
        body: formData
    });

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
