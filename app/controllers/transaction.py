from typing import Any, List, Optional


async def get_account_transactions(
    account_id: str,
    from_date: Optional[str] = None,
    to_date: Optional[str] = None
) -> List[Any]:    # Replace this with the entity that we will create
    """
    1. Check if we internally have account transactions for these dates
    2. If we have fetch and return them
    3. If we don't
        1. Fetch the transactions from nordigen
        2. Save the transactions internally
        3. Update AccountHistory model
        4. Return the transactions
    """
    pass