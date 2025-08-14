from sqladmin import ModelView

from ..auth.model import User


class UserAdmin(ModelView, model=User):
    """View-модель пользователя для SQL админки"""
    column_list = [
        User.id,
        User.username,
        User.email,
        User.is_superuser,
        User.is_active,
        User.created_at,
        User.updated_at,
    ]
    can_create = False
    can_edit = False
    can_delete = True