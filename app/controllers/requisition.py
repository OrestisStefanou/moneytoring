from typing import List
from sqlmodel.ext.asyncio.session import AsyncSession

from app.services import requisition as requisition_service
from app.services import institution as institution_service
from app.services import bank_account as bank_account_service
from app.utils import requisition as requisition_utils
from app.entities.requisition import BankConnection, BankAccount
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
