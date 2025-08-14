from fastapi import APIRouter, Depends, Response, status

from ..auth.dependencies import current_admin_user
from ..auth.model import User
from ..exceptions import HttpForbiddenException
from ..utils import ok_response_docs, error_response_docs

admin_router = APIRouter(
    prefix="/auth",
    tags=["admin"]
)


@admin_router.get(
    '/protected',
    name="protected",
    summary="Защита admin роута",
    description=
    """
    При переходе/отправке запроса к роутам /admin* на этот роут приходит запрос на проверку доступа
    """,
    status_code=status.HTTP_200_OK,
    responses={
        **ok_response_docs(
            status_code=status.HTTP_200_OK,
            description='Пользователь прошел проверку на admin'
        ),
        **error_response_docs(
            error=HttpForbiddenException
        ),
    }
)
async def protected(admin_user: User = Depends(current_admin_user)):
    if not admin_user:
        raise HttpForbiddenException
    return Response(status_code=200)
