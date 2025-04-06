const API_BASE_URL_AUTH = 'http://localhost:5000/api/user';

const errorMessageElement = document.getElementById('error-message');

function checkAuthStatus() {
    const token = localStorage.getItem('token');
    if (token) {
        if (window.location.pathname.includes('/login') || 
            window.location.pathname.includes('/signup')) {
            window.location.href = './';
        }
        return true;
    }
    return false;
}

function updateAuthUI() {
    const userControls = document.querySelector('.user-controls');
    const token = localStorage.getItem('token');
    
    if (token) {
        userControls.innerHTML = `
            <div class="dropdown">
                <a class="user-profile">My Account</a>
                <div class="dropdown-menu">
                    <a href="/profile">My Profile</a>
                    <a href="#" id="logout-button">Logout</a>
                </div>
            </div>
        `;
        
        document.getElementById('logout-button').addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('token');
            window.location.href = './';
        });
    } else {
        userControls.innerHTML = `
            <a href="/login" class="login-btn">Login</a>
            <a href="/signup" class="signup-btn">Sign Up</a>
        `;
    }

    userControls.classList.add('visible');
}

if (document.getElementById('login-form')) {
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        errorMessageElement.style.display = 'none';
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch(`${API_BASE_URL_AUTH}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Login failed');
            }
            
            localStorage.setItem('token', data.token);

            updateAuthUI();
            
            window.location.href = './';
            
        } catch (error) {
            errorMessageElement.textContent = error.message;
            errorMessageElement.style.display = 'block';
        }
    });
}

if (document.getElementById('signup-form')) {
    document.getElementById('signup-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        errorMessageElement.style.display = 'none';
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        if (password !== confirmPassword) {
            errorMessageElement.textContent = 'Passwords do not match';
            errorMessageElement.style.display = 'block';
            return;
        }
        
        try {
            const response = await fetch(`${API_BASE_URL_AUTH}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ email, password })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || 'Registration failed');
            }
            
            window.location.href = '/login?registered=true';
            
        } catch (error) {
            errorMessageElement.textContent = error.message;
            errorMessageElement.style.display = 'block';
        }
    });
}

document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    
    if (urlParams.get('registered') === 'true' && errorMessageElement) {
        errorMessageElement.textContent = 'Registration successful! Please log in.';
        errorMessageElement.style.display = 'block';
        errorMessageElement.className = 'success-message';
    }
    
    checkAuthStatus();
    
    updateAuthUI();
});