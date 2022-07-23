from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services import requisition as requisition_service
from app.services import institution as institution_service
from app.entities.requisition import BankConnection
from app.errors.institution import InstitutionNotFound


async def create_bank_connection(
    session: AsyncSession,
    user_id: str,
    institution_id: str,
    redirect_uri: str
) -> BankConnection:
    institution = await institution_service.get_institution_by_id(institution_id)
    if institution is None:
        raise InstitutionNotFound()

    # Create a requisition on Nordigen side
    nordigen_requisition = await requisition_service.create_nordigen_requisition(institution_id, redirect_uri)

    # Create internal requisition
    internal_requisition = await requisition_service.create_internal_requisition(
        session=session,
        _id=nordigen_requisition.id,
        user_id=user_id,
        institution_id=institution_id,
        institution_name=institution.name,
        link=nordigen_requisition.link
    )

    # Return BankConnection entity
    return BankConnection(
        id=internal_requisition.id,
        institution_name=internal_requisition.institution_name,
        link=internal_requisition.link
    )


async def get_user_bank_connections(
    session: AsyncSession,
    user_id: str
) -> List[BankConnection]:
    user_requisitions = await requisition_service.get_requisitions_of_user(session, user_id)
    for requisition in user_requisitions:
        if requisition.status == "not_linked":
            # Fetch requisition from nordigen to check for status update
            pass

        # Get requisition's accounts and stuff
        
