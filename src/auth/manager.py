import uuid
from typing import Optional

from fastapi import Request, Response
from fastapi.responses import RedirectResponse
from fastapi_users import BaseUserManager, UUIDIDMixin
from loguru import logger

from .model import User


class UserManager(UUIDIDMixin, BaseUserManager[User, uuid.UUID]):
    """Менеджер пользователей для обработки событий аутентификации.

    Наследует функциональность от BaseUserManager и UUIDIDMixin для работы с UUID.
    Обрабатывает события после регистрации и входа пользователя.

    Attributes:
        reset_password_token_secret: Секрет для токена сброса пароля
        verification_token_secret: Секрет для токена верификации

    Methods:
        on_after_register: Вызывается после успешной регистрации пользователя
        on_after_login: Вызывается после успешного входа пользователя
    """

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        """Обработчик события после регистрации пользователя.

        Args:
            user: Зарегистрированный пользователь
            request: Объект запроса FastAPI (опционально)

        Returns:
            RedirectResponse: Перенаправление на страницу входа
        """
        logger.info(f"Пользователь {user} зарегистрирован")
        return RedirectResponse('/login')

    async def on_after_login(
        self,
        user: User,
        request: Optional[Request] = None,
        response: Optional[Response] = None,
    ):
        """Обработчик события после входа пользователя.

        Args:
            user: Аутентифицированный пользователь
            request: Объект запроса FastAPI (опционально)
            response: Объект ответа FastAPI (опционально)

        Returns:
            RedirectResponse: Перенаправление на главную страницу
        """
        logger.info(f"Пользователь {user} вошел")
        return RedirectResponse('/')
