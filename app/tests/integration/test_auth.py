import pytest
from app.tests.fixtures import test_client, test_db, event_loop, async_session
from app.repos.app_user_repo import AppUserRepo

class TestSignUp:
    @pytest.mark.asyncio
    async def test_successful_signup(
        self,
        test_client,
        test_db,
        async_session
    ):
        response = test_client.post(
            "/signup",
            json={"username": "orestis", "email": "orestis@email.com", "password": "12345"},
        )   
        assert response.status_code == 201
        user_repo = AppUserRepo(async_session)
        user = await user_repo.get_by_email("orestis@email.com")
        assert user.username == "orestis"
        assert user.password != "12345"     # Make sure the password is hashed

    @pytest.mark.asyncio
    async def test_email_unavailable(
        self,
        test_client,
        test_db,
        async_session
    ):
        response = test_client.post(
            "/signup",
            json={"username": "orestis", "email": "orestis@email.com", "password": "12345"},
        )   
        assert response.status_code == 201

        response = test_client.post(
            "/signup",
            json={"username": "orestis", "email": "orestis@email.com", "password": "12345"},
        )   
        assert response.status_code == 400
        assert response.json()['detail'] == "User with this email already exists"

        user_repo = AppUserRepo(async_session)
        users = await user_repo.get_all()
        assert len(users) == 1

    @pytest.mark.asyncio
    async def test_invalid_email(
        self,
        test_client,
        test_db,
        async_session
    ):
        response = test_client.post(
            "/signup",
            json={"username": "orestis", "email": "orestis.com", "password": "12345"},
        )   
        assert response.status_code == 400
        assert response.json()['detail'] == "Invalid email"
        
        user_repo = AppUserRepo(async_session)
        users = await user_repo.get_all()
        assert users == []

class TestToken:
    def test_successful(
        self,
        test_client,
        test_db
    ):
        response = test_client.post(
            "/signup",
            json={"username": "orestis", "email": "orestis@email.com", "password": "12345"},
        )   
        assert response.status_code == 201

        response = test_client.post(
            "/token",
            data={"username": "orestis@email.com", "password": "12345"},
        )

        assert response.status_code == 200

    def test_authentication_error(
        self,
        test_client,
        test_db
    ):
        response = test_client.post(
            "/token",
            data={"username": "orestis@email.com", "password": "12345"},
        )   

        assert response.status_code == 401
        assert response.json()['detail'] == 'Wrong email or password'
