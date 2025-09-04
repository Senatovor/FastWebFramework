from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse

from .dependencies import current_user
from .model import User
from ..config import templates

auth_templates = APIRouter(
    tags=["templates"],
)


@auth_templates.get(
    '/login',
    name='login_template',
    summary='Страница авторизации',
    response_class=HTMLResponse,
)
async def login_template(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='/auth/login.html',
    )


@auth_templates.get(
    '/register',
    name='register_template',
    summary='Страница регистрации',
    response_class=HTMLResponse,
)
async def login_template(request: Request):
    return templates.TemplateResponse(
        request=request,
        name='/auth/register.html',
    )


@auth_templates.get(
    '/',
    name='home',
    summary='Домашняя страница',
    response_class=HTMLResponse,
)
async def login_template(request: Request, user: User = Depends(current_user)):
    return templates.TemplateResponse(
        request=request,
        name='home.html',
        context={
            'user': user,
        }
    )
