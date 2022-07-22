from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.repos.sql_repo import SQLRepo
from app.models.database.requisition import Requisition


class RequisitionRepo(SQLRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=Requisition)
    
    async def add(
        self,
        _id: str,
        user_id: str,
        institution_id: str,
        institution_name: str,
        link: str
    ):
        requisition = Requisition(
            id=_id,
            user_id=user_id,
            institution_id=institution_id,
            institution_name=institution_name,
            link=link
        )

        self._session.add(requisition)
        await self._session.commit()
        return requisition