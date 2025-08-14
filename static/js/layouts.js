document.addEventListener('DOMContentLoaded', function () {
    // Находим все кнопки выхода по классу
    document.querySelectorAll('.logout-link').forEach(link => {
        link.addEventListener('click', async function (e) {
            e.preventDefault(); // Отменяем переход по ссылке

            // Получаем CSRF-токен из куки
            const csrftoken = getCookie('csrftoken');

            if (!csrftoken) {
                console.error('CSRF токен не найден');
                window.location.href = '/login';
                return;
            }

            try {
                // Отправляем POST запрос на выход с CSRF-токеном
                const response = await fetch('/auth/jwt/logout', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': csrftoken
                    },
                    credentials: 'include' // Для передачи куков
                });

                // Перенаправляем на страницу входа независимо от ответа сервера
                window.location.href = '/login';

            } catch (error) {
                console.error('Ошибка при выходе:', error);
                window.location.href = '/login'; // Перенаправляем даже при ошибке
            }
        });
    });

    // Функция для получения куки по имени
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});