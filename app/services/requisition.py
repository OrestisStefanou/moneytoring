from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.requisition_repo import RequisitionRepo
from app.repos.nordigen_repo import NordigenRepo
import app.models.http.nordigen as nordigen_models
import app.models.database.requisition as db_requisition


async def create_nordigen_requisition(institution_id: str, redirect_uri: str) -> nordigen_models.Requisition:
    nordigen_repo = NordigenRepo()
    nordigen_requisition = await nordigen_repo.create_requisition(institution_id, redirect_uri)
    return nordigen_requisition


async def get_requisition_from_nordigen(requisition_id: str) -> Optional[nordigen_models.Requisition]:
    nordigen_repo = NordigenRepo()
    requisition = await nordigen_repo.get_requisition_by_id(requisition_id)
    return requisition


async def get_requisitions_of_user(session: AsyncSession, user_id: str) -> List[db_requisition.Requisition]:
    requisition_repo = RequisitionRepo(session)
    user_requisitions = await requisition_repo.get_requisitions_of_user(user_id) 
    return [
        requisition for requisition in user_requisitions
    ]


async def create_internal_requisition(
    session: AsyncSession,
    _id: str,
    user_id: str,
    institution_id: str,
    institution_name: str,
    link: str
) -> db_requisition.Requisition:
    requisition_repo = RequisitionRepo(session)
    requisition = await requisition_repo.add(
        _id=_id,
        user_id=user_id,
        institution_id=institution_id,
        institution_name=institution_name,
        link=link
    )
    return requisition


async def mark_internal_requisition_as_linked(
    session: AsyncSession,
    requisition_id: str,
    created_at: str,
    expires_at: str,
    max_historical_days: int
) -> db_requisition.Requisition:
    requisition_repo = RequisitionRepo(session)
    requisition = await requisition_repo.set_linked_status_info(
        _id=requisition_id,
        created_at=created_at,
        expires_at=expires_at,
        max_historical_days=max_historical_days
    )
    return requisition