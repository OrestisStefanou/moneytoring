from typing import Optional
import uuid

from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.repos.sql_repo import SQLRepo
from app.models.database.app_user import AppUser


class AppUserRepo(SQLRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=AppUser)

    async def add_user(self, username: str, email: str, password: str):
        app_user = AppUser(
            user_id=str(uuid.uuid4()),
            username=username,
            email=email,
            password=password
        )
        self._session.add(app_user)
        await self._session.commit()


    async def get_by_email(self, email: str) -> Optional[AppUser]:
        statement = select(AppUser).where(AppUser.email == email)
        result = await self._session.exec(statement)
        return result.first()
