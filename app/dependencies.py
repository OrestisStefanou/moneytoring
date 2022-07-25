from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app import settings
from app.http.nordigen_client import NordigenClient


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
engine = create_async_engine(settings.database_dsn, connect_args={"check_same_thread": False})
nordigen_client = NordigenClient()

async def get_session():
    async_session = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        await session.exec("PRAGMA foreign_keys = ON")  # THIS SHOULD BE DELETED WHEN WE TRANSITION FROM SQLITE
        yield session


async def extract_user_id_from_token(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = jwt.decode(token, settings.oauth2_secret_key, algorithms=[settings.oauth2_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return user_id