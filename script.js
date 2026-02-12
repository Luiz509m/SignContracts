const API_URL = "https://signcontracts-lastcall.onrender.com/analyze";

async function uploadContract() {
    const fileInput = document.getElementById("fileInput");
    const loading = document.getElementById("loading");
    const result = document.getElementById("result");
    
    // TOKEN PRÜFEN
    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert("Bitte zuerst einloggen!");
        window.location.href = 'upload.html';
        return;
    }
    
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
            headers: {
                'Authorization': `Bearer ${token}`  // TOKEN HIER!
            },
            body: formData
        });
        
        const text = await response.text();
        let data;
        
        try {
            data = JSON.parse(text);
        } catch {
            throw new Error("Backend hat kein JSON geliefert");
        }
        
        // Wenn 401 Unauthorized -> ausloggen
        if (response.status === 401) {
            alert("Sitzung abgelaufen. Bitte neu einloggen.");
            localStorage.removeItem('auth_token');
            window.location.href = 'upload.html';
            return;
        }
        
        // 🔴 Ampel
        const ampelValue = data.ampel || "unbekannt";
        const ampel = document.getElementById("ampel");
        ampel.innerText = "AMPEL: " + ampelValue.toUpperCase();
        ampel.className = "ampel " + ampelValue;
        
        // 🔴 Risiken
        const risiken = document.getElementById("risiken");
        risiken.innerHTML = "";
        (data.top_risiken || []).forEach(r => {
            const li = document.createElement("li");
            li.innerText = r.beschreibung || r;
            risiken.appendChild(li);
        });
        
        // 🔴 Empfehlungen
        const empfehlungen = document.getElementById("empfehlungen");
        empfehlungen.innerHTML = "";
        (data.empfehlungen || []).forEach(e => {
            const li = document.createElement("li");
            li.innerText = e;
            empfehlungen.appendChild(li);
        });
        
        // 🔴 Mail
        document.getElementById("mail").value = data.mail?.text || "";
        
        loading.style.display = "none";
        result.style.display = "block";
        
    } catch (err) {
        loading.style.display = "none";
        alert("Analyse fehlgeschlagen – siehe Konsole");
        console.error("FEHLER:", err);
    }
}
