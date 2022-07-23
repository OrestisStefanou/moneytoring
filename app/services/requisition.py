from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.requisition_repo import RequisitionRepo
from app.repos.nordigen_repo import NordigenRepo
import app.models.http.nordigen as nordigen_models
import app.models.database.requisition as db_requisition


async def create_nordigen_requisition(institution_id: str, redirect_uri: str) -> nordigen_models.Requisition:
    nordigen_repo = NordigenRepo()
    nordigen_requisition = await nordigen_repo.create_requisition(institution_id, redirect_uri)
    return nordigen_requisition


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