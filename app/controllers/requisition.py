from typing import List

from sqlmodel.ext.asyncio.session import AsyncSession

from app.services import requisition as requisition_service
from app.services import institution as institution_service
from app.services import bank_account as bank_account_service
from app.utils import requisition as requisition_utils
from app.entities.requisition import BankConnection, BankAccount
from app.errors.institution import InstitutionNotFound
from app.errors.requisition import BankConnectionNotFound
from app.errors.nordigen import RequisitionNotFound
from app.models.database.requisition import Requisition as DbRequisition


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
    bank_connections = []
    user_requisitions = await requisition_service.get_requisitions_of_user(session, user_id)
    for requisition in user_requisitions:
        requistion_bank_accounts = await bank_account_service.get_requistion_bank_accounts(
            session=session,
            requisition_id=requisition.id
        )

        bank_connections.append(
            BankConnection(
                id=requisition.id,
                institution_name=requisition.institution_name,
                link=requisition.link,
                accepted_at=requisition.accepted_at,
                expires_at=requisition.expires_at,
                max_historical_days=requisition.max_historical_days,
                status=requisition_utils.map_req_status_to_bank_conn_status(requisition.status),
                bank_accounts=[
                    BankAccount(
                        account_id=bank_account.account_id,
                        name=bank_account.name,
                        currency=bank_account.currency
                    )
                    for bank_account in requistion_bank_accounts
                ]
            )
        )

    return bank_connections


async def delete_bank_connection(session: AsyncSession, bank_connection_id: str) -> DbRequisition:
    try:
        await requisition_service.delete_requisition_from_nordigen(bank_connection_id)
    except RequisitionNotFound:
        """
        We don't raise an exception here yet to cover the case that the requisition
        was deleted from nordigen but not on our side(This could happen if for some reason when
        we deleted the requisition from nordigen the function call below failed)
        """
        pass
        
    deleted_requisition = await requisition_service.delete_internal_requisition(
        session=session,
        requisition_id=bank_connection_id
    )

    if deleted_requisition is None:
        raise BankConnectionNotFound()
    
    return deleted_requisition


async def update_expired_bank_connection(session: AsyncSession, bank_connection_id: str, user_id: str) -> BankConnection:
    """
    What happens here
    1. Delete requisition from nordigen
    2. Delete the internal requisition
    3. Create a new requisition in nordigen for the same bank
    4. Create an internal requisition
    5. Send back the new bank connection
    """
    deleted_requisition = await delete_bank_connection(session, bank_connection_id)
    new_bank_connection = await create_bank_connection(
        session=session,
        user_id=user_id,
        institution_id=deleted_requisition.institution_id,
        redirect_uri=deleted_requisition.link
    )

    return new_bank_connection
