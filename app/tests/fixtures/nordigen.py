from datetime import datetime, timedelta
from typing import List, Optional
import pytest

from pytest_httpx import HTTPXMock


@pytest.fixture(scope="function")
def nordigen_token(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://ob.nordigen.com/api/v2/token/new/",
        method="POST",
        json={
            "access": "test_access",
            "access_expires": 100,
            "refresh": "test_refresh",
            "refresh_expires": 100
        }
    )


def mock_nordigen_get_country_institutions(httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="https://ob.nordigen.com/api/v2/institutions/?country=CY",
        method="GET",
        json=[
            {
                "id": "ASTROBANK_PIRBCY2N",
                "name": "AstroBank",
                "bic": "PIRBCY2N",
                "transaction_total_days": "730",
                "countries": [
                "CY"
                ],
                "logo": "astrobank_logo"
            },
            {
                "id": "BANKOFCYPRUS_BCYPCY2NXXX",
                "name": "Bank of Cyprus",
                "bic": "BCYPCY2NXXX",
                "transaction_total_days": "730",
                "countries": [
                "CY"
                ],
                "logo": "https://cdn.nordigen.com/ais/BANKOFCYPRUS_BCYPCY2NXXX.png"
            },
        ],
        status_code=200,
    )


def mock_get_nordigen_country_institutions_400(httpx_mock: HTTPXMock, country_code: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/institutions/?country={country_code}",
        method="GET",
        json={},
        status_code=400,
    )


def mock_nordigen_get_institution_by_id(httpx_mock: HTTPXMock, institution_id: str, institution_name: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/institutions/{institution_id}/",
        method="GET",
        json={
            "id": institution_id,
            "name": institution_name,
            "bic": "PIRBCY2N",
            "transaction_total_days": "730",
            "countries": [
            "CY"
            ],
            "logo": "astrobank_logo"
        },
        status_code=200,
    )


def mock_nordigen_get_institution_by_id_not_found(httpx_mock: HTTPXMock, institution_id: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/institutions/{institution_id}/",
        method="GET",
        json={},
        status_code=404,
    )


def mock_create_nordigen_requisition(
    httpx_mock: HTTPXMock,
    institution_id: str,
    requisition_id: str
):
    httpx_mock.add_response(
        url="https://ob.nordigen.com/api/v2/requisitions/",
        method="POST",
        json={
            "id": requisition_id,
            "created": "2022-07-26T09:44:24.664Z",
            "redirect": "www.some_website.com",
            "status": "CR",
            "institution_id": institution_id,
            "agreement": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
            "reference": None,
            "accounts": [],
            "user_language": "klingon",
            "link": "https://ob.nordigen.com/psd2/start/3fa85f64-5717-4562-b3fc-2c963f66afa6/anavarkos_bank",
            "ssn": "string",
            "account_selection": False,
            "redirect_immediate": False
        },
        status_code=201
    )


def mock_get_requisition_with_linked_status(
    httpx_mock: HTTPXMock,
    requisition_id: str,
    institution_id: Optional[str] = "SANDBOXFINANCE_SFIN0000",
    accounts: Optional[List[str]] = None,
    agreement_id: Optional[str] = "3eef47d9-99e8-4a05-88a1-39f95ed84fad"
):
    if accounts is None:
        accounts = [
            "7e944232-bda9-40bc-b784-660c7ab5fe78",
            "99a0bfe2-0bef-46df-bff2-e9ae0c6c5838"
        ]

    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/requisitions/{requisition_id}/",
        method="GET",
        json={
            "id": requisition_id,
            "created": "2022-07-25T19:15:20.624770Z",
            "redirect": "https://www.some_website.com",
            "status": "LN",
            "institution_id": institution_id,
            "agreement": agreement_id,
            "reference": "d2dee8cf-e9c3-4e72-afd6-ae5f801a3ab5",
            "accounts": accounts,
            "link": "https://ob.nordigen.com/psd2/start/d2dee8cf-e9c3-4e72-afd6-ae5f801a3ab5/SANDBOXFINANCE_SFIN0000",
            "ssn": None,
            "account_selection": None,
            "redirect_immediate": None
            },
        status_code=200
    )


def mock_get_account_details(httpx_mock: HTTPXMock, account_id: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/accounts/{account_id}/details/",
        method="GET",
        json={
            "account": {
                "resourceId": "01F3NS4YV94RA29YCH8R0F6BMF",
                "iban": "GL3343697694912188",
                "currency": "EUR",
                "ownerName": "Lionel Messi",
                "name": "Main Account",
                "product": "Checkings",
                "cashAccountType": "CACC"
            }
        },
        status_code=200
    )


def mock_get_nordigen_agreement(httpx_mock: HTTPXMock, agreement_id: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/agreements/enduser/{agreement_id}/",
        method="GET",
        json={
            "id": "3eef47d9-99e8-4a05-88a1-39f95ed84fad",
            "created": "2022-07-25T19:15:40.234163Z",
            "max_historical_days": 90,
            "access_valid_for_days": 90,
            "access_scope": [
                "balances",
                "details",
                "transactions"
            ],
            "accepted": "2022-07-25",
            "institution_id": "SANDBOXFINANCE_SFIN0000"
        },
        status_code=200
    )


def mock_delete_nordigen_requisition(httpx_mock: HTTPXMock, requisition_id: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/requisitions/{requisition_id}/",
        method="DELETE",
        json={},
        status_code=200
    )


def mock_delete_nordigen_requisition_not_found(httpx_mock: HTTPXMock, requisition_id: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/requisitions/{requisition_id}/",
        method="DELETE",
        json={},
        status_code=404
    )


def mock_get_account_transactions(httpx_mock: HTTPXMock, account_id: str):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/accounts/{account_id}/transactions/",
        method="GET",
        json={
        "transactions": {
            "booked": [
                {
                    "transactionId": f"{account_id}-1",
                    "bookingDate": "2022-08-14",
                    "valueDate": "2022-08-14",
                    "transactionAmount": {
                        "amount": "45.00",
                        "currency": "EUR"
                    },
                    "debtorName": "MON MOTHMA",
                    "debtorAccount": {
                        "iban": "GL3343697694912188"
                    },
                    "remittanceInformationUnstructured": "For the support of Restoration of the Republic foundation",
                    "bankTransactionCode": "PMNT"
                },
                {
                    "transactionId": f"{account_id}-2",
                    "bookingDate": "2022-08-15",
                    "valueDate": "2022-08-14",
                    "transactionAmount": {
                        "amount": "-15.00",
                        "currency": "EUR"
                    },
                    "remittanceInformationUnstructured": "PAYMENT Alderaan Coffe",
                    "bankTransactionCode": "PMNT"
                },
                {
                    "transactionId": f"{account_id}-3",
                    "bookingDate": "2022-08-13",
                    "valueDate": "2022-08-14",
                    "transactionAmount": {
                        "amount": "45.00",
                        "currency": "EUR"
                    },
                    "debtorName": "MON MOTHMA",
                    "debtorAccount": {
                        "iban": "GL3343697694912188"
                    },
                    "remittanceInformationUnstructured": "For the support of Restoration of the Republic foundation",
                    "bankTransactionCode": "PMNT"
                },
                {
                    "transactionId": f"{account_id}-4",
                    "bookingDate": "2022-08-12",
                    "valueDate": "2022-08-14",
                    "transactionAmount": {
                        "amount": "-15.00",
                        "currency": "EUR"
                    },
                    "remittanceInformationUnstructured": "PAYMENT Alderaan Coffe",
                    "bankTransactionCode": "PMNT"
                },
            ],
            "pending": [
                {
                    "valueDate": "2022-08-13",
                    "transactionAmount": {
                    "amount": "10.00",
                    "currency": "EUR"
                    },
                    "remittanceInformationUnstructured": "Reserved PAYMENT Emperor's Burgers"
                }
            ]
        }
        },
        status_code=200
    )


def mock_get_account_transactions_wtih_dates(
    httpx_mock: HTTPXMock,
    account_id: str,
    date_from: str,
):
    httpx_mock.add_response(
        url=f"https://ob.nordigen.com/api/v2/accounts/{account_id}/transactions/?date_from={date_from}",
        method="GET",
        json={
        "transactions": {
            "booked": [
                {
                    "transactionId": f"{account_id}-1",
                    "bookingDate": date_from,
                    "valueDate": date_from,
                    "transactionAmount": {
                        "amount": "45.00",
                        "currency": "EUR"
                    },
                    "debtorName": "MON MOTHMA",
                    "debtorAccount": {
                        "iban": "GL3343697694912188"
                    },
                    "remittanceInformationUnstructured": "For the support of Restoration of the Republic foundation",
                    "bankTransactionCode": "PMNT"
                },
                {
                    "transactionId": f"{account_id}-2",
                    "bookingDate": date_from,
                    "valueDate": date_from,
                    "transactionAmount": {
                        "amount": "-15.00",
                        "currency": "EUR"
                    },
                    "remittanceInformationUnstructured": "PAYMENT Alderaan Coffe",
                    "bankTransactionCode": "PMNT"
                },
            ],
            "pending": [
                {
                    "valueDate": "2022-08-13",
                    "transactionAmount": {
                    "amount": "10.00",
                    "currency": "EUR"
                    },
                    "remittanceInformationUnstructured": "Reserved PAYMENT Emperor's Burgers"
                }
            ]
        }
        },
        status_code=200
    )
