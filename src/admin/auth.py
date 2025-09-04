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
    async def login(self, request: Request):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)

    async def logout(self, request: Request):
        backend = AuthBackend.get_auth_backend()
        strategy = backend.get_strategy()

        user, token = await self._get_user_token(request)

        response = await backend.logout(strategy, user, token)

        response.headers["Location"] = config.BASE_URL
        response.status_code = status.HTTP_307_TEMPORARY_REDIRECT

        return response

    async def authenticate(self, request: Request) -> bool:
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
        return request.cookies.get("access_token")

    @session_manager.connection(commit=False)
    async def _get_user_token(self, request: Request, session):
        token = await self._extract_token(request)
        if not token:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        backend = AuthBackend.get_auth_backend()
        strategy = backend.get_strategy()

        user_table = SQLAlchemyUserDatabase(session, User)
        user_manager = UserManager(user_table)

        user = await strategy.read_token(token, user_manager)

        return user, token
