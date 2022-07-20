from datetime import datetime, timedelta
from typing import Any, Dict, Optional
from sqlmodel.ext.asyncio.session import AsyncSession
from jose import jwt
from app.models.database.app_user import AppUser

from app.repos.app_user_repo import AppUserRepo
from app.utils import auth as auth_utils
from app import settings


async def check_email_availability(session: AsyncSession, email: str) -> bool:
    """
    Check if user with given email already exists
    Returns True if email is available, False otherwise
    """
    app_user_repo = AppUserRepo(session=session)
    app_user = await app_user_repo.get_by_email(email)
    if app_user is not None:
        return False
    
    return True


async def create_app_user(session: AsyncSession, username: str, email:str, password: str) -> None:
    app_user_repo = AppUserRepo(session=session)
    await app_user_repo.add_user(username=username, email=email, password=auth_utils.get_password_hash(password))


async def get_authenticated_user(session: AsyncSession, email: str, password: str) -> Optional[AppUser]:
    app_user_repo = AppUserRepo(session=session)
    app_user = await app_user_repo.get_by_email(email)

    if app_user is None:
        return None

    if not auth_utils.verify_password(password, app_user.password):
        return None
    
    return app_user


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Create and return a jwt string"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.oauth2_secret_key, algorithm=settings.oauth2_algorithm)
    return encoded_jwt
