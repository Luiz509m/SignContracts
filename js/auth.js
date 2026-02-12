// Token Management
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
