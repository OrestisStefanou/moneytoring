from app.tests.fixtures import test_client, test_db

class TestSignUp:
    def test_successful_signup(
        self,
        test_client,
        test_db
    ):
        response = test_client.post(
            "/signup",
            json={"username": "orestis", "email": "orestis@email.com", "password": "12345"},
        )   
        assert response.status_code == 201


    def test_email_unavailable(
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
            "/signup",
            json={"username": "orestis", "email": "orestis@email.com", "password": "12345"},
        )   
        assert response.status_code == 400
        assert response.json()['detail'] == "User with this email already exists"


    def test_invalid_email(
        self,
        test_client,
        test_db
    ):
        response = test_client.post(
            "/signup",
            json={"username": "orestis", "email": "orestis.com", "password": "12345"},
        )   
        assert response.status_code == 400
        assert response.json()['detail'] == "Invalid email"
    

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