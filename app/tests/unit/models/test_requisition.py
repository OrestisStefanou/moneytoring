from app.models.database.requisition import Requisition

def test_expires_at():
    requisition = Requisition(
        id="test_id",
        user_id="darth_vader",
        institution_id="anavarkos_bank_id",
        institution_name="anavarkos_bank",
        link="some_link",
        expires_at="2021-08-01"
    )

    assert requisition.is_expired is True

    requisition.expires_at="2050-09-01"
    assert requisition.is_expired is False
