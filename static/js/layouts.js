document.addEventListener('DOMContentLoaded', function() {
    // Находим все кнопки выхода по классу
    document.querySelectorAll('.logout-link').forEach(link => {
        link.addEventListener('click', async function(e) {
            e.preventDefault(); // Отменяем переход по ссылке

            try {
                // Отправляем POST запрос на выход
                const response = await fetch('/auth/jwt/logout', {
                    method: 'POST',
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
});