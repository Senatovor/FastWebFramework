import uuid

from fastapi_users import schemas
from pydantic import BaseModel, Field


class Username(BaseModel):
    """Модель для username"""
    username: str = Field(
        min_length=1,
        max_length=20,
        description='Имя пользователя'
    )


class UserRead(schemas.BaseUser[uuid.UUID], Username):
    """Модель пользователя для чтения"""
    pass


class UserCreate(schemas.BaseUserCreate, Username):
    """Модель пользователя для создания"""
    pass
