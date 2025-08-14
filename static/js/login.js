document.addEventListener('DOMContentLoaded', function () {
    const loginForm = document.getElementById('loginForm');

    loginForm.addEventListener('submit', handleLoginSubmit);

    async function handleLoginSubmit(e) {
        e.preventDefault();
        const form = e.target;

        const formData = new URLSearchParams();
        formData.append('grant_type', 'password');
        formData.append('username', document.getElementById('username').value);
        formData.append('password', document.getElementById('password').value);
        formData.append('csrftoken', form.csrftoken.value);

        try {
            const response = await fetch('/auth/jwt/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': form.csrftoken.value
                },
                body: formData,
                credentials: 'include'
            });

            handleLoginResponse(response);
        } catch (error) {
            handleLoginError(error);
        }
    }

    async function handleLoginResponse(response) {
        if (response.ok) {
            showToast('Вход выполнен успешно', 'success');
            setTimeout(() => window.location.href = '/', 1500);
        } else if (response.status === 400) {
            const error = await response.json();
            const message = error.detail === 'LOGIN_BAD_CREDENTIALS'
                ? 'Неверное имя пользователя или пароль'
                : error.detail;
            showToast(message, 'danger');
        } else if (response.status === 422) {
            const errors = await response.json();
            showToast('Ошибка валидации: ' + errors.detail.map(e => e.msg).join(', '), 'danger');
        } else {
            showToast(`Ошибка сервера: ${response.status}`, 'danger');
        }
    }

    function handleLoginError(error) {
        console.error('Ошибка сети:', error);
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