from datetime import timedelta
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services import auth as auth_services
from app.errors import auth as auth_erros
from app.utils import auth as auth_utils
from app import settings
from app.entities.auth_token import Token

async def create_user(session: AsyncSession, email: str , username: str, password: str):
    if auth_utils.email_is_valid(email) is False:
        raise auth_erros.InvalidEmail()

    email_available = await auth_services.check_email_availability(session, email)
    if email_available is False:
        raise auth_erros.EmailUnavailable()
    
    # TODO Check password strength
    await auth_services.create_app_user(session=session, username=username, email=email, password=password)


async def create_token(session: AsyncSession, email: str , password: str) -> Token:
    authenticated_user = await auth_services.get_authenticated_user(session, email, password)
    if not authenticated_user:
        raise auth_erros.AuthenticationError()
    
    token = auth_services.create_access_token(
        data={"sub": authenticated_user.user_id},
        expires_delta= timedelta(minutes=settings.access_token_expire_minutes)
    )

    return Token(
        access_token=token,
        token_type="bearer"
    )