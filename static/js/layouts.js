document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.logout-link').forEach(link => {
        link.addEventListener('click', async function(e) {
            e.preventDefault();

            // 1. Достаём CSRF-токен из скрытого input
            const csrfTokenInput = document.querySelector('#csrfForm input[name="csrftoken"]');
            if (!csrfTokenInput) {
                console.error('CSRF-токен не найден в DOM');
                window.location.href = '/login';
                return;
            }
            const csrfToken = csrfTokenInput.value;

            // 2. Отправляем запрос через fetch (как и раньше)
            try {
                const response = await fetch('/auth/jwt/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrfToken  // Используем токен из формы
                    },
                    credentials: 'include'
                });

                // 3. Перенаправляем после выхода
                window.location.href = '/login';

            } catch (error) {
                console.error('Ошибка при выходе:', error);
                window.location.href = '/login';
            }
        });
    });
});