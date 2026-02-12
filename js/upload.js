const API_BASE = "https://signcontracts-lastcall.onrender.com";

// ==================== TOKEN MANAGEMENT ====================
function saveToken(token) {
    localStorage.setItem('auth_token', token);
}

function getToken() {
    return localStorage.getItem('auth_token');
}

function clearToken() {
    localStorage.removeItem('auth_token');
}

function isLoggedIn() {
    return !!getToken();
}

// ==================== PAGE LOAD ====================
window.addEventListener('DOMContentLoaded', () => {
    // Wenn schon eingeloggt -> direkt zum Dashboard
    if (isLoggedIn()) {
        showDashboard();
    }
});

// ==================== TAB SWITCHING ====================
function switchTab(tab) {
    const loginForm = document.getElementById('login-form');
    const registerForm = document.getElementById('register-form');
    const tabs = document.querySelectorAll('.tab');
    
    clearMessages();
    
    if (tab === 'login') {
        loginForm.classList.add('active');
        registerForm.classList.remove('active');
        tabs[0].classList.add('active');
        tabs[1].classList.remove('active');
    } else {
        loginForm.classList.remove('active');
        registerForm.classList.add('active');
        tabs[0].classList.remove('active');
        tabs[1].classList.add('active');
    }
}

// ==================== LOGIN ====================
async function handleLogin(event) {
    event.preventDefault();
    clearMessages();
    
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    
    try {
        const response = await fetch(`${API_BASE}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            // Token speichern
            saveToken(data.token);
            
            // Zum Dashboard
            showDashboard(data.user);
        } else {
            showError(data.detail || 'Login fehlgeschlagen');
        }
    } catch (error) {
        showError('Netzwerkfehler - bitte versuchen Sie es erneut');
    }
}

// ==================== REGISTER ====================
async function handleRegister(event) {
    event.preventDefault();
    clearMessages();
    
    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const passwordConfirm = document.getElementById('register-password-confirm').value;
    
    if (password !== passwordConfirm) {
        showError('Passwörter stimmen nicht überein');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showSuccess('Registrierung erfolgreich! Bitte melden Sie sich an.');
            switchTab('login');
            
            // Felder leeren
            document.getElementById('register-name').value = '';
            document.getElementById('register-email').value = '';
            document.getElementById('register-password').value = '';
            document.getElementById('register-password-confirm').value = '';
        } else {
            showError(data.detail || 'Registrierung fehlgeschlagen');
        }
    } catch (error) {
        showError('Netzwerkfehler - bitte versuchen Sie es erneut');
    }
}

// ==================== LOGOUT ====================
async function logout() {
    const token = getToken();
    if (token) {
        try {
            await fetch(`${API_BASE}/auth/logout`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
        } catch (error) {
            console.log('Logout Fehler:', error);
        }
    }
    clearToken();
    window.location.reload();
}

// ==================== SHOW DASHBOARD ====================
function showDashboard(user) {
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('dashboard-screen').style.display = 'block';
    
    // Username anzeigen (falls vorhanden)
    if (user) {
        document.getElementById('userName').textContent = user.name || user.email;
    }
}

// ==================== FILE HANDLING ====================
function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSelected').style.display = 'flex';
        document.getElementById('analyzeBtn').disabled = false;
    }
}

function removeFile() {
    document.getElementById('fileInput').value = '';
    document.getElementById('fileSelected').style.display = 'none';
    document.getElementById('analyzeBtn').disabled = true;
}

// ==================== ANALYZE CONTRACT ====================
async function analyzeContract() {
    const fileInput = document.getElementById('fileInput');
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    const token = getToken();
    if (!token) {
        alert("Sitzung abgelaufen. Bitte neu anmelden.");
        logout();
        return;
    }
    
    if (!fileInput.files.length) {
        alert("Bitte wählen Sie eine Datei aus");
        return;
    }
    
    const formData = new FormData();
    formData.append("file", fileInput.files[0]);
    
    loading.style.display = 'block';
    results.style.display = 'none';
    
    try {
        const response = await fetch(`${API_BASE}/analyze`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData
        });
        
        if (response.status === 401) {
            alert("Sitzung abgelaufen. Bitte neu einloggen.");
            logout();
            return;
        }
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.detail || 'Analyse fehlgeschlagen');
        }
        
        displayResults(data);
        
    } catch (error) {
        alert(`Fehler bei der Analyse: ${error.message}`);
        console.error('Analyse Fehler:', error);
    } finally {
        loading.style.display = 'none';
    }
}

// ==================== DISPLAY RESULTS ====================
function displayResults(data) {
    const results = document.getElementById('results');
    const ampelIcon = document.getElementById('ampelIcon');
    const ampelText = document.getElementById('ampelText');
    const ampelDescription = document.getElementById('ampelDescription');
    
    // Ampel
    const ampel = data.ampel || 'gelb';
    ampelText.textContent = ampel.toUpperCase();
    ampelText.className = 'ampel-text ampel-' + ampel;
    
    if (ampel === 'rot') {
        ampelIcon.textContent = '🔴';
        ampelDescription.textContent = 'Hohe Risiken identifiziert - Vorsicht geboten';
    } else if (ampel === 'gelb') {
        ampelIcon.textContent = '🟡';
        ampelDescription.textContent = 'Mittlere Risiken - Prüfung empfohlen';
    } else {
        ampelIcon.textContent = '🟢';
        ampelDescription.textContent = 'Geringe Risiken - Vertrag erscheint akzeptabel';
    }
    
    // Risiken
    const risikenList = document.getElementById('risikenList');
    risikenList.innerHTML = '';
    (data.top_risiken || []).forEach(risiko => {
        const li = document.createElement('li');
        li.textContent = risiko.beschreibung || risiko;
        risikenList.appendChild(li);
    });
    
    // Empfehlungen
    const empfehlungenList = document.getElementById('empfehlungenList');
    empfehlungenList.innerHTML = '';
    (data.empfehlungen || []).forEach(emp => {
        const li = document.createElement('li');
        li.textContent = emp;
        empfehlungenList.appendChild(li);
    });
    
    // Mail
    const mailPreview = document.getElementById('mailPreview');
    if (data.mail && data.mail.text) {
        mailPreview.innerHTML = `<pre>${data.mail.text}</pre>`;
    } else {
        mailPreview.textContent = 'Keine E-Mail-Vorlage verfügbar';
    }
    
    results.style.display = 'block';
}

// ==================== RESET ANALYSIS ====================
function resetAnalysis() {
    removeFile();
    document.getElementById('results').style.display = 'none';
}

// ==================== MESSAGES ====================
function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
}

function showSuccess(message) {
    const successDiv = document.getElementById('success');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
}

function clearMessages() {
    document.getElementById('error').style.display = 'none';
    document.getElementById('success').style.display = 'none';
}
