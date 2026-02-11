// Backend URL - WICHTIG: Deine Render-URL hier eintragen!
const API_URL = 'https://signcontracts-lastcall.onrender.com';

// ==================== AUTH FUNCTIONS ====================

function switchTab(tab) {
    // Update tabs
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    event.target.classList.add('active');

    // Update forms
    document.querySelectorAll('.form-container').forEach(f => f.classList.remove('active'));
    document.getElementById(tab + '-form').classList.add('active');

    // Clear messages
    hideMessages();
}

function showError(message) {
    const errorDiv = document.getElementById('error');
    errorDiv.textContent = message;
    errorDiv.style.display = 'block';
    document.getElementById('success').style.display = 'none';
}

function showSuccess(message) {
    const successDiv = document.getElementById('success');
    successDiv.textContent = message;
    successDiv.style.display = 'block';
    document.getElementById('error').style.display = 'none';
}

function hideMessages() {
    document.getElementById('error').style.display = 'none';
    document.getElementById('success').style.display = 'none';
}

async function handleRegister(event) {
    event.preventDefault();
    hideMessages();

    const name = document.getElementById('register-name').value;
    const email = document.getElementById('register-email').value;
    const password = document.getElementById('register-password').value;
    const passwordConfirm = document.getElementById('register-password-confirm').value;

    if (password !== passwordConfirm) {
        showError('Passwörter stimmen nicht überein');
        return;
    }

    try {
        const response = await fetch(`${API_URL}/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ name, email, password })
        });

        const data = await response.json();

        if (response.ok) {
            showSuccess('Registrierung erfolgreich! Sie können sich jetzt anmelden.');
            setTimeout(() => {
                switchTab('login');
                document.getElementById('login-email').value = email;
            }, 1500);
        } else {
            showError(data.detail || 'Registrierung fehlgeschlagen');
        }
    } catch (error) {
        showError('Verbindung zum Server fehlgeschlagen. Backend läuft möglicherweise nicht.');
        console.error('Register error:', error);
    }
}

async function handleLogin(event) {
    event.preventDefault();
    hideMessages();

    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;

    try {
        const response = await fetch(`${API_URL}/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });

        const data = await response.json();

        if (response.ok) {
            // Save token and user
            localStorage.setItem('token', data.token);
            localStorage.setItem('user', JSON.stringify(data.user));
            
            // Show dashboard
            showDashboard();
        } else {
            showError(data.detail || 'Login fehlgeschlagen');
        }
    } catch (error) {
        showError('Verbindung zum Server fehlgeschlagen. Backend läuft möglicherweise nicht.');
        console.error('Login error:', error);
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    showAuthScreen();
}

function showDashboard() {
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    document.getElementById('userName').textContent = user.name || user.email;
    
    document.getElementById('auth-screen').style.display = 'none';
    document.getElementById('dashboard-screen').style.display = 'block';
}

function showAuthScreen() {
    document.getElementById('auth-screen').style.display = 'flex';
    document.getElementById('dashboard-screen').style.display = 'none';
    
    // Reset forms
    document.querySelectorAll('form').forEach(f => f.reset());
    hideMessages();
}

// ==================== FILE UPLOAD FUNCTIONS ====================

let selectedFile = null;

function handleFileSelect(event) {
    selectedFile = event.target.files[0];
    if (selectedFile) {
        document.getElementById('fileName').textContent = selectedFile.name;
        document.getElementById('fileSelected').classList.add('active');
        document.getElementById('analyzeBtn').disabled = false;
    }
}

function removeFile() {
    selectedFile = null;
    document.getElementById('fileInput').value = '';
    document.getElementById('fileSelected').classList.remove('active');
    document.getElementById('analyzeBtn').disabled = true;
}

async function analyzeContract() {
    if (!selectedFile) {
        alert('Bitte wählen Sie eine PDF-Datei aus');
        return;
    }

    const formData = new FormData();
    formData.append('file', selectedFile);

    document.querySelector('.upload-container').style.display = 'none';
    document.getElementById('loading').classList.add('active');
    document.getElementById('results').classList.remove('active');

    try {
        const token = localStorage.getItem('token');
        
        // Timeout Controller - 120 Sekunden
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 120000);
        
        const response = await fetch(`${API_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            },
            body: formData,
            signal: controller.signal
        });

        clearTimeout(timeoutId);

        const data = await response.json();

        document.getElementById('loading').classList.remove('active');

        if (response.ok) {
            displayResults(data);
        } else {
            alert('Fehler bei der Analyse: ' + (data.detail || 'Unbekannter Fehler'));
            document.querySelector('.upload-container').style.display = 'block';
        }
    } catch (error) {
        document.getElementById('loading').classList.remove('active');
        document.querySelector('.upload-container').style.display = 'block';
        
        if (error.name === 'AbortError') {
            alert('Analyse-Timeout: Die Analyse dauerte zu lange. Bitte versuchen Sie es mit einem kürzeren Vertrag erneut.');
        } else {
            alert('Verbindung zum Server fehlgeschlagen. Stellen Sie sicher, dass das Backend läuft.');
        }
        console.error('Analysis error:', error);
    }
}

function displayResults(data) {
    document.getElementById('results').classList.add('active');

    // Ampel
    const ampelIcons = { gruen: '🟢', gelb: '🟡', rot: '🔴' };
    const ampelTexts = { gruen: 'GRÜN - UNAUFFÄLLIG', gelb: 'GELB - PRÜFBEDARF', rot: 'ROT - KRITISCH' };
    const ampelDescriptions = {
        gruen: 'Ihr Vertrag ist unauffällig. Die wichtigsten Punkte sind klar geregelt.',
        gelb: 'Ihr Vertrag enthält Punkte, die Sie genauer prüfen sollten.',
        rot: 'Achtung! Ihr Vertrag enthält kritische Punkte, die vor Unterschrift geklärt werden sollten.'
    };

    document.getElementById('ampelIcon').textContent = ampelIcons[data.ampel] || '🚦';
    document.getElementById('ampelText').textContent = ampelTexts[data.ampel] || 'BEWERTUNG';
    document.getElementById('ampelText').className = `ampel-text ${data.ampel}`;
    document.getElementById('ampelDescription').textContent = ampelDescriptions[data.ampel] || '';

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
    document.getElementById('mailPreview').textContent = data.mail?.text || 'Keine E-Mail-Vorlage verfügbar';
}

function resetAnalysis() {
    document.getElementById('results').classList.remove('active');
    document.querySelector('.upload-container').style.display = 'block';
    removeFile();
}

// ==================== DRAG & DROP ====================

window.addEventListener('DOMContentLoaded', () => {
    // Check if user is already logged in
    const token = localStorage.getItem('token');
    if (token) {
        showDashboard();
    }

    // Drag and drop support
    const uploadArea = document.querySelector('.upload-area');
    
    if (uploadArea) {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.style.borderColor = '#ff8c42';
                uploadArea.style.transform = 'scale(1.02)';
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.style.borderColor = '#ffc099';
                uploadArea.style.transform = 'scale(1)';
            });
        });

        uploadArea.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                const file = files[0];
                if (file.type === 'application/pdf') {
                    document.getElementById('fileInput').files = files;
                    handleFileSelect({ target: { files: [file] } });
                } else {
                    alert('Bitte laden Sie nur PDF-Dateien hoch');
                }
            }
        });
    }
});
