import pytest

from app.http.nordigen_client import NordigenClient


@pytest.mark.asyncio
async def test_get_agreement():
    client = NordigenClient()
    agreement = await client.get_agreement_by_id('36a31839-d8bf-4001-9030-306f38d233b2')
    print(agreement)