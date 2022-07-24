from typing import List, Optional
from sqlmodel.ext.asyncio.session import AsyncSession

from app.repos.requisition_repo import RequisitionRepo
from app.repos.nordigen_repo import NordigenRepo
import app.models.http.nordigen as nordigen_models
import app.models.database.requisition as db_requisition
import app.utils.nordigen as nordigen_utils
from app.services import bank_account as bank_account_service


async def create_nordigen_requisition(institution_id: str, redirect_uri: str) -> nordigen_models.Requisition:
    nordigen_repo = NordigenRepo()
    nordigen_requisition = await nordigen_repo.create_requisition(institution_id, redirect_uri)
    return nordigen_requisition


async def fetch_requisition_from_nordigen(requisition_id: str) -> Optional[nordigen_models.Requisition]:
    nordigen_repo = NordigenRepo()
    requisition = await nordigen_repo.get_requisition_by_id(requisition_id)
    return requisition


async def get_requisitions_of_user(session: AsyncSession, user_id: str) -> List[db_requisition.Requisition]:
    requisition_repo = RequisitionRepo(session)
    internal_requisitions = await requisition_repo.get_requisitions_of_user(user_id) 
    user_requisitions = []
    for internal_requisition in internal_requisitions:
        if internal_requisition.status == db_requisition.RequisitionStatus.not_linked:
            print("FETCHING REQUISITIONS FROM NORDGIEN")
            # Fetch requistion from nordigen to check for status update
            nordigen_requisition = await fetch_requisition_from_nordigen(internal_requisition.id)
            if nordigen_requisition.status == "LN":
                print("UPDATING INTERNAL REQUISITIONS")
                # Status is updated to linked so we have to update ours internally
                internal_requisition = await mark_internal_requisition_as_linked(
                    session=session,
                    requisition_id=internal_requisition.id,
                    agreement_id=nordigen_requisition.agreement_id
                )
                print("FETCHING THE ACCOUNTS")
                # Fetch the requisition's account from nordigen
                for account_id in nordigen_requisition.accounts:
                    account_details = await bank_account_service.get_account_details_from_nordigen(account_id)
                    # Create a bank account internally
                    await bank_account_service.create_internal_bank_account(
                        session=session,
                        account_id=account_id,
                        requistion_id=internal_requisition.id,
                        name=account_details.name,
                        currency=account_details.currency
                    )
        user_requisitions.append(internal_requisition)

    return user_requisitions


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
    agreement_id: str,
) -> db_requisition.Requisition:
    # Fetch agreement info from nordigen
    nordigen_repo = NordigenRepo()
    agreement = await nordigen_repo.get_agreement_by_id(agreement_id)
    
    requisition_repo = RequisitionRepo(session)
    requisition = await requisition_repo.set_linked_status_info(
        _id=requisition_id,
        accepted_at=agreement.accepted,
        expires_at=nordigen_utils.calculate_expiration_date(
            accepted_datetime_str=agreement.accepted,
            days_duration=agreement.access_valid_for_days
        ),
        max_historical_days=agreement.max_historical_days
    )
    return requisition