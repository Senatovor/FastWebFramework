from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTableUUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String

from ..database.model import Base


class User(SQLAlchemyBaseUserTableUUID, Base):
    """Модель ORM пользователя"""
    username: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        unique=True,
        comment='Логин пользователя'
    )
