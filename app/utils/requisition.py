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
