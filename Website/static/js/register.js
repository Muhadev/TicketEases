document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registerForm');
    
    form.addEventListener('submit', function(event) {
        // Perform client-side validation
        let valid = true;

        const username = document.getElementById('username');
        const email = document.getElementById('email');
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm-password');
        
        // Reset error messages
        username.classList.remove('is-invalid');
        email.classList.remove('is-invalid');
        password.classList.remove('is-invalid');
        confirmPassword.classList.remove('is-invalid');

        if (username.value.trim().length < 4) {
            valid = false;
            username.classList.add('is-invalid');
            document.getElementById('username-error').innerText = 'Username must be at least 4 characters long.';
        }

        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        if (!emailPattern.test(email.value.trim())) {
            valid = false;
            email.classList.add('is-invalid');
            document.getElementById('email-error').innerText = 'Invalid email format.';
        }

        const passwordPattern = /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d]{8,}$/;
        if (!passwordPattern.test(password.value.trim())) {
            valid = false;
            password.classList.add('is-invalid');
            document.getElementById('password-error').innerText = 'Password must be at least 8 characters long and include both letters and numbers.';
        }

        if (password.value.trim() !== confirmPassword.value.trim()) {
            valid = false;
            confirmPassword.classList.add('is-invalid');
            document.getElementById('confirm-password-error').innerText = 'Passwords do not match.';
        }

        if (!valid) {
            event.preventDefault();
            event.stopPropagation();
        }
    }, false);
});
