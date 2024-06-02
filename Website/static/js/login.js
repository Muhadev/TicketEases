document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('loginForm');

    form.addEventListener('submit', function (event) {
        event.preventDefault();
        event.stopPropagation();

        let isValid = true;

        const email = document.getElementById('email');
        const password = document.getElementById('password');
        // Clear previous error messages
        clearError(email);
        clearError(password);

        // Validate Email
        if (!email.value) {
            isValid = false;
            setError(email, 'Email is required.');
        } else if (!validateEmail(email.value)) {
            isValid = false;
            setError(email, 'Invalid email format.');
        }

        // Validate Password
        if (!password.value) {
            isValid = false;
            setError(password, 'Password is required.');
        } else if (password.value.length < 8) {
            isValid = false;
            setError(password, 'Password must be at least 8 characters long.');
        }

        if (isValid) {
            form.classList.add('was-validated');
            form.submit();
        } else {
            form.classList.add('was-validated');
        }
    });

    function setError(element, message) {
        const errorElement = document.createElement('div');
        errorElement.className = 'invalid-feedback';
        errorElement.innerText = message;
        element.classList.add('is-invalid');
        element.parentNode.appendChild(errorElement);
    }

    function clearError(element) {
        const errorElements = element.parentNode.querySelectorAll('.invalid-feedback');
        errorElements.forEach(el => el.remove());
        element.classList.remove('is-invalid');
    }

    function validateEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    }
});
