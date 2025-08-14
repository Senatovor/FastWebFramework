import uuid
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import CookieTransport, AuthenticationBackend
import redis.asyncio
from fastapi_users.authentication import RedisStrategy
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase

from ..config import config
from .manager import UserManager
from .model import User
from ..database.session import DbSessionDepends

class AuthBackend:
    """Конфигурация системы аутентификации FastAPI Users.

     Содержит настройки для:
    - Redis-клиента для хранения токенов
    - Cookie-транспорта для передачи токенов
    - Redis-стратегии аутентификации
    - Бэкенда аутентификации

    Args:
        redis_client: Асинхронный клиент Redis для хранения токенов
        cookie_transport: Настройки передачи токена через cookies
    """

    redis_client = redis.asyncio.from_url(
        config.redis_config.redis_url,
        decode_responses=True
    )

    cookie_transport = CookieTransport(
        cookie_name='access_token',
        cookie_path='/',
        cookie_httponly=True,
        cookie_secure=True,
        cookie_samesite='lax',
        cookie_max_age=3600
    )

    @classmethod
    def get_redis_strategy(cls) -> RedisStrategy:
        """Создает и возвращает стратегию хранения токенов в Redis.

        Returns:
            RedisStrategy: Стратегия аутентификации с использованием Redis
        """
        return RedisStrategy(
            cls.redis_client,
            lifetime_seconds=3600,
            key_prefix='access_token',
        )

    @classmethod
    def get_auth_backend(cls) -> AuthenticationBackend:
        """Возвращает backend авторизации.

        Returns:
            AuthenticationBackend: backend авторизации
        """
        return AuthenticationBackend(
            name='jwt',
            transport=cls.cookie_transport,
            get_strategy=cls.get_redis_strategy,
        )


async def get_user_table(session: DbSessionDepends(commit=True)):
    """Зависимость для получения таблицы пользователей.

    Args:
        session: Асинхронная сессия SQLAlchemy

    Yields:
        SQLAlchemyUserDatabase: Объект для работы с таблицей пользователей
    """
    yield SQLAlchemyUserDatabase(session, User)


async def get_user_manager(user_db = Depends(get_user_table)):
    """Зависимость для получения менеджера пользователей.

    Args:
        user_db: Зависимость таблицы пользователей

    Yields:
        UserManager: Менеджер для работы с пользователями
    """
    yield UserManager(user_db)


fastapi_users_modul = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [AuthBackend.get_auth_backend()],
)
