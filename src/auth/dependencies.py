from .backend import fastapi_users_modul

current_user = fastapi_users_modul.current_user()   # Зависимость для получения текущего юзера

current_admin_user = fastapi_users_modul.current_user(superuser=True)   # Зависимость для получения текущего админа
