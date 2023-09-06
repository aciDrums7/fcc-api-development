import pytest
from tests.conftest import client
from app.authentication import oauth2_service
from app.schemas.token_schemas import Token
from app.schemas.users_schemas import UserOut
from app.utils.password_utils import verify_password

test_email = "test@email.com"
test_password = "testpassword"


@pytest.fixture
def test_user(client):
    new_user_data = {"email": test_email, "password": test_password}
    res = client.post("/users", json=new_user_data)
    assert res.status_code == 201
    new_user = res.json()
    new_user["plain_password"] = new_user_data["password"]
    return new_user


def test_hello_world(client):
    res = client.get("/")
    print(res.json())
    assert res.json() == "Hello World!"
    assert res.status_code == 200


def test_create_user(client):
    res = client.post("/users", json={"email": test_email, "password": test_password})
    print(res.json())
    new_user = UserOut(**res.json())
    assert new_user.email == test_email
    assert verify_password(test_password, new_user.password)
    assert res.status_code == 201


def test_login_user(client, test_user):
    res = client.post(
        "/login",
        data={"username": test_user["email"], "password": test_user["plain_password"]},
    )
    print(res.json())
    new_token = Token(**res.json())
    token_payload = oauth2_service.verify_jwt_and_return_payload(new_token.access_token)
    print(token_payload)

    assert token_payload is not None
    assert test_user['id'] == token_payload.user_id
    assert new_token.token_type == "Bearer"
    assert res.status_code == 200
