// API endpoint configuration
const API_BASE_URL = 'http://localhost:5001/api/user';

// DOM Elements
const errorMessageElement = document.getElementById('error-message');

// Check if user is already logged in
function checkAuthStatus() {
    const token = localStorage.getItem('token');
    if (token) {
        // If on login/signup page, redirect to home
        if (window.location.pathname.includes('login.html') || 
            window.location.pathname.includes('signup.html')) {
            window.location.href = 'index.html';
        }
        return true;
    }
    return false;
}

// Update UI based on authentication state
function updateAuthUI() {
    const userControls = document.querySelector('.user-controls');
    const token = localStorage.getItem('token');
    
    if (token) {
        // User is logged in, update the UI
        userControls.innerHTML = `
            <div class="dropdown">
                <a class="user-profile">My Account</a>
                <div class="dropdown-menu">
                    <a href="profile.html">My Profile</a>
                    <a href="#" id="logout-button">Logout</a>
                </div>
            </div>
        `;
        
        // Add event listener to logout button
        document.getElementById('logout-button').addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('token');
            window.location.href = 'index.html';
        });
    } else {
        // User is not logged in
        userControls.innerHTML = `
            <a href="login.html" class="login-btn">Login</a>
            <a href="signup.html" class="signup-btn">Sign Up</a>
        `;
    }
}

// Handle login form submission
if (document.getElementById('login-form')) {
    document.getElementById('login-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        errorMessageElement.style.display = 'none';
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        try {
            const response = await fetch(`${API_BASE_URL}/login`, {
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
            
            // Store token in localStorage
            localStorage.setItem('token', data.token);

            updateAuthUI();
            
            // Redirect to homepage
            window.location.href = 'index.html';
            
        } catch (error) {
            errorMessageElement.textContent = error.message;
            errorMessageElement.style.display = 'block';
        }
    });
}

// Handle signup form submission
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
            const response = await fetch(`${API_BASE_URL}/register`, {
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
            
            // Redirect to login page
            window.location.href = 'login.html?registered=true';
            
        } catch (error) {
            errorMessageElement.textContent = error.message;
            errorMessageElement.style.display = 'block';
        }
    });
}

// Handle URL parameters for success messages
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    
    // Check for successful registration
    if (urlParams.get('registered') === 'true' && errorMessageElement) {
        errorMessageElement.textContent = 'Registration successful! Please log in.';
        errorMessageElement.style.display = 'block';
        errorMessageElement.className = 'success-message';
    }
    
    // Check auth status on page load
    checkAuthStatus();
    
    // Update UI based on authentication
    updateAuthUI();
});