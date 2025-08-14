from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import httpx

from ..config import config
from ..exceptions import HttpServerException


class AdminAuthMiddleware(BaseHTTPMiddleware):
    """Middleware для аутентификации администраторских маршрутов.

    Перехватывает запросы к маршрутам, начинающимся с /admin, и проверяет аутентификацию
    пользователя, делая запрос к защищенному эндпоинту. В случае неудачной аутентификации
    возвращает соответствующую ошибку.

     Пример использования: app.add_middleware(AdminAuthMiddleware)
    """
    async def dispatch(self, request: Request, call_next):
        """Обрабатывает входящий запрос и проверяет аутентификацию для /admin маршрутов.

        Args:
            request: Входящий HTTP-запрос
            call_next: Функция для вызова следующего middleware/обработчика

        Returns:
            Response: Ответ либо от следующего обработчика, либо ошибка аутентификации

        Raises:
            HTTPException(403): При отказе в доступе
            HTTPException(503): При недоступности сервиса аутентификации
        """
        # Проверяем только /admin роуты
        if request.url.path.startswith("/admin"):
            try:
                # Создаем клиент для запроса к защищенному эндпоинту
                async with httpx.AsyncClient() as client:
                    # Копируем куки и заголовки из оригинального запроса
                    headers = dict(request.headers)
                    cookies = dict(request.cookies)

                    # Отправляем запрос к защищенному эндпоинту
                    response = await client.get(
                        f"{config.BASE_URL}auth/protected",
                        headers=headers,
                        cookies=cookies
                    )

                    # Если доступ запрещен
                    if response.status_code != 200:
                        raise HTTPException(
                            status_code=response.status_code,
                            detail=response.json().get("detail")
                        )

            except httpx.RequestError:
                raise HttpServerException
            except HTTPException as e:
                return JSONResponse(
                    status_code=e.status_code,
                    content={"detail": e.detail}
                )

        return await call_next(request)