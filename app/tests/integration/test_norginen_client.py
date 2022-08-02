import pytest

from app.http.nordigen_client import NordigenClient


@pytest.mark.asyncio
async def test_get_agreement():
    client = NordigenClient()
    transactions = await client.get_account_transactions(
        account_id="7e944232-bda9-40bc-b784-660c7ab5fe78",
        date_from="2022-07-20"
    )
    print(transactions)