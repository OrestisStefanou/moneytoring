from typing import Iterable, Optional

from requests import session
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from app.repos.sql_repo import SQLRepo
from app.models.database.requisition import Requisition, RequisitionStatus


class RequisitionRepo(SQLRepo):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, model=Requisition)
    
    async def add(
        self,
        _id: str,
        user_id: str,
        institution_id: str,
        institution_name: str,
        link: str,
        status: Optional[RequisitionStatus] = RequisitionStatus.not_linked
    ) -> Requisition:
        requisition = Requisition(
            id=_id,
            user_id=user_id,
            institution_id=institution_id,
            institution_name=institution_name,
            link=link,
            status=status
        )

        self._session.add(requisition)
        await self._session.commit()
        return requisition

    async def get_requisitions_of_user(self, user_id: str) -> Iterable[Requisition]:
        statement = select(Requisition).where(Requisition.user_id == user_id)
        user_requisitions = await self._session.exec(statement)
        return user_requisitions

    async def set_linked_status_info(
        self,
        _id: str,
        accepted_at: str,
        expires_at: str,
        max_historical_days: str
    ) -> Requisition:
        """
        Updates requisition's status to linked and sets
        relevant information about the linking duration
        """
        requisition = await self.get(_id)
        requisition.status = RequisitionStatus.linked
        requisition.accepted_at = accepted_at
        requisition.expires_at = expires_at
        requisition.max_historical_days = max_historical_days

        self._session.add(requisition)
        await self._session.commit()
        await self._session.refresh(requisition)
        return requisition

    async def delete_requisition_by_id(self, _id: str) -> Optional[Requisition]:
        """
        Returns the deleted requisition or None in case the requisition doesn't exist
        """
        requisition = await self.get(_id)
        if requisition is None:
            return None

        await self._session.delete(requisition)
        await self._session.commit()
        return requisition
