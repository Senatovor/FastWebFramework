from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from loguru import logger
from sqladmin.authentication import AuthenticationBackend
from fastapi import Request, HTTPException, status

from ..auth.backend import AuthBackend
from ..auth.manager import UserManager
from ..auth.model import User
from ..config import config
from ..database.session import session_manager


class AdminAuth(AuthenticationBackend):
    """
    Класс аутентификации для административной панели SQLAdmin.

    Наследуется от AuthenticationBackend и предоставляет методы для:
    - Входа в систему (login)
    - Выхода из системы (logout) 
    - Проверки аутентификации (authenticate)

    Использует JWT токены из cookies для проверки прав доступа.
    """

    async def login(self, request: Request):
        """
        Обработчик входа в систему.

        Args:
            request (Request): HTTP запрос

        Raises:
            HTTPException: Всегда возвращает 404 Not Found
        """
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    async def logout(self, request: Request):
        """
        Обработчик выхода из системы.

        Выполняет выход пользователя и перенаправляет на базовый URL.

        Args:
            request (Request): HTTP запрос

        Returns:
            Response: Ответ с перенаправлением и очисткой cookies

        Raises:
            HTTPException: Если токен не найден или невалиден
        """
        backend = AuthBackend.get_auth_backend()
        strategy = backend.get_strategy()

        user, token = await self._get_user_token(request)

        response = await backend.logout(strategy, user, token)

        response.headers["Location"] = config.BASE_URL
        response.status_code = status.HTTP_307_TEMPORARY_REDIRECT

        return response

    async def authenticate(self, request: Request) -> bool:
        """
        Проверяет аутентификацию пользователя и права доступа.

        Args:
            request (Request): HTTP запрос

        Returns:
            bool: True если пользователь аутентифицирован и имеет права суперпользователя

        Raises:
            HTTPException: 403 если нет прав доступа, 401 если не аутентифицирован
            Exception: Логирует и пробрасывает другие ошибки
        """
        try:
            user, _ = await self._get_user_token(request)

            if user and user.is_active and user.is_superuser:
                return True
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)

        except Exception as e:
            logger.error(f"Проблема при авторизации в админку: {e}")
            raise e

    @staticmethod
    async def _extract_token(request: Request) -> str:
        """
        Извлекает JWT токен из cookies запроса.

        Args:
            request (Request): HTTP запрос

        Returns:
            str: Токен доступа или None если не найден
        """
        return request.cookies.get("access_token")

    @session_manager.connection(commit=False)
    async def _get_user_token(self, request: Request, session):
        """
        Получает пользователя по JWT токену из запроса.

        Использует менеджер сессий для работы с базой данных.

        Args:
            request (Request): HTTP запрос
            session: Сессия базы данных

        Returns:
            tuple: (user, token) - пользователь и токен

        Raises:
            HTTPException: 401 если токен не предоставлен или невалиден
        """
        token = await self._extract_token(request)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        backend = AuthBackend.get_auth_backend()
        strategy = backend.get_strategy()

        user_table = SQLAlchemyUserDatabase(session, User)
        user_manager = UserManager(user_table)

        user = await strategy.read_token(token, user_manager)

        return user, token