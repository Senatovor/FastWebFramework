document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');

    registerForm.addEventListener('submit', handleRegisterSubmit);

    async function handleRegisterSubmit(e) {
        e.preventDefault();

        const formData = {
            username: document.getElementById('username').value,
            email: document.getElementById('email').value,
            password: document.getElementById('password').value,
            is_active: true,
            is_superuser: false,
            is_verified: false
        };

        try {
            const response = await fetch('/auth/register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            handleRegisterResponse(response);
        } catch (error) {
            handleRegisterError(error);
        }
    }

    async function handleRegisterResponse(response) {
        if (response.status === 201) {
            const userData = await response.json();
            showToast(`Пользователь ${userData.username} успешно зарегистрирован`, 'success');
            setTimeout(() => window.location.href = '/login', 1500);
        }
        else if (response.status === 400) {
            const error = await response.json();
            const message = error.detail === 'REGISTER_USER_ALREADY_EXISTS'
                ? 'Пользователь с таким email уже существует'
                : error.detail;
            showToast(message, 'danger');
        }
        else if (response.status === 422) {
            const errors = await response.json();
            showToast('Ошибка валидации: ' + errors.detail.map(e => e.msg).join(', '), 'danger');
        }
        else {
            showToast(`Ошибка сервера: ${response.status}`, 'danger');
        }
    }

    function handleRegisterError(error) {
        console.error('Ошибка:', error);
        showToast('Не удалось подключиться к серверу', 'danger');
    }

    // Общие функции для уведомлений
    function showToast(message, type = 'success') {
        const toastContainer = document.getElementById('toastContainer') || createToastContainer();
        const toast = document.createElement('div');

        toast.className = `toast show align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        toastContainer.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    }

    function createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'position-fixed bottom-0 end-0 p-3';
        container.style.zIndex = '11';
        document.body.appendChild(container);
        return container;
    }
});