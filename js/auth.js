// Token Management für SignContracts
const API_BASE = "https://signcontracts-lastcall.onrender.com";

// Token speichern
function saveToken(token) {
    localStorage.setItem('auth_token', token);
}

// Token abrufen
function getToken() {
    return localStorage.getItem('auth_token');
}

// Token löschen
function clearToken() {
    localStorage.removeItem('auth_token');
}

// Ist User eingeloggt?
function isLoggedIn() {
    return !!getToken();
}

// Login Funktion
async function login(email, password) {
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
            return { success: true, user: data.user };
        } else {
            return { success: false, error: data.detail || 'Login fehlgeschlagen' };
        }
    } catch (error) {
        return { success: false, error: 'Netzwerkfehler' };
    }
}

// Register Funktion
async function register(name, email, password) {
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
            return { success: true };
        } else {
            return { success: false, error: data.detail || 'Registrierung fehlgeschlagen' };
        }
    } catch (error) {
        return { success: false, error: 'Netzwerkfehler' };
    }
}

// Logout Funktion
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
    window.location.href = 'index.html';
}
