import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pathlib import Path
from contextlib import asynccontextmanager
from sqladmin import Admin
from asgi_csrf import asgi_csrf

from src.admin.middleware import AdminAuthMiddleware
from src.admin.models import UserAdmin
from src.admin.router import admin_router
from src.auth.backend import fastapi_users_modul, AuthBackend
from src.auth.templates import auth_templates
from src.redis_database.client import redis_manager
from src.database.session import session_manager
from src.log import setup_logger
from src.config import config
from src.auth.schemes import UserRead, UserCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Контекстный менеджер жизненного цикла приложения FastAPI.

     Управляет инициализацией и освобождением ресурсов:
    - Инициализация Redis соединения
    - Инициализация соединения с базой данных
    - Настройка административной панели
    - Очистка ресурсов при завершении

    Args:
        app: Экземпляр FastAPI приложения

    Yields:
        None: Возвращает управление приложению
    """

    # Инициализация пулов redis
    await redis_manager.init()
    app.state.redis_manager = redis_manager

    # Инициализация сессий sql базы
    await session_manager.init()
    app.state.db_manager = session_manager

    admin = Admin(app, session_manager.engine)
    admin.add_view(UserAdmin)

    yield

    # Очистка
    await redis_manager.close()
    await session_manager.close()


def create_app() -> FastAPI:
    """Фабрика для создания и конфигурации FastAPI приложения.

    Returns:
        FastAPI: Настроенный экземпляр FastAPI приложения

     Конфигурация включает:
    - Базовые метаданные (название, версия, описание)
    - CORS политики
    - Подключение статических файлов
    - Регистрацию маршрутов аутентификации
    - Подключение административных маршрутов
    - Добавление middleware для аутентификации администраторов
    - Добавление csrf защиты
    """
    app = FastAPI(
        title=config.TITLE,
        version=config.VERSION,
        description=config.description_project,
        contact=config.contact_project,
        docs_url=config.DOCS_URL,
        redoc_url=config.REDOC_URL,
        root_path=config.ROOT_PATH,
        lifespan=lifespan
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    )
    app.mount('/static', StaticFiles(directory=Path(__file__).parent.parent / 'static'), name='static')
    app.include_router(
        fastapi_users_modul.get_auth_router(AuthBackend.get_auth_backend()),
        prefix="/auth/jwt",
        tags=["auth"],
    )
    app.include_router(
        fastapi_users_modul.get_register_router(UserRead, UserCreate),
        prefix="/auth",
        tags=["auth"],
    )
    app.include_router(admin_router)
    app.include_router(auth_templates)
    app.add_middleware(AdminAuthMiddleware)
    csrf_protected_app = asgi_csrf(
        app,
        signing_secret="your-secret-key-here",
        always_set_cookie=True,
        cookie_name="csrftoken",
        cookie_path="/",
        cookie_domain=None,
        cookie_secure=False,
        cookie_samesite="Lax",
        always_protect={
            "/auth/jwt/login",
            '/auth/jwt/logout',
            '/auth/register',
            '/auth/protected',
        }
    )
    return csrf_protected_app


if __name__ == '__main__':
    """Точка входа для запуска приложения.

     Выполняет:
    - Настройку системы логирования
    - Создание экземпляра приложения
    - Запуск сервера Uvicorn

    Raises:
        Exception: Логирует любые ошибки при запуске приложения
    """
    try:
        setup_logger()
        app = create_app()
        uvicorn.run(
            app,
            host="0.0.0.0",
            port=5000,
            log_config=None,
            log_level=None,
        )

    except Exception as e:
        logger.error(f'Во время создания приложения произошла ошибка: {e}')
