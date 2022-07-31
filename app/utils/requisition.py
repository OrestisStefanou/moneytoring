from datetime import datetime, timedelta

from app.models.database.requisition import RequisitionStatus
from app.entities.requisition import BankConnectionStatus

def map_req_status_to_bank_conn_status(req_status: RequisitionStatus):
    if req_status == RequisitionStatus.linked:
        return BankConnectionStatus.created
    
    if req_status == RequisitionStatus.not_linked:
        return BankConnectionStatus.pending

    if req_status == RequisitionStatus.expired:
        return BankConnectionStatus.expired


def check_expiration(expiration_date_string: str) -> bool:
    """
    - Params:
        - expiration_date_string: Date in string format YYYY-MM-DD
    - Returns:
        - True if expiration date is before current date
        - False if expiration date is after current date
    """
    expiration_dt = datetime.strptime(expiration_date_string, "%Y-%m-%d")

    if expiration_dt > datetime.now():
        return False
    
    return True