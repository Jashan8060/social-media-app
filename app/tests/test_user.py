import pytest
from jose import jwt
from app import schemas

from app.config import settings



def test_greet(client):
    res = client.get("/")
    # print(res.json())
    # # print("hello")
    assert res.status_code == 200

def test_user_create(client):
    res = client.post("/users/", json={"email": "test@gmail.com", "password": "test123"})
    print(res.json())
    assert res.status_code == 201


def test_login_user(test_user, client):
    res = client.post(
        "/login", data={"username": test_user['email'], "password": test_user['password']})
    login_res = schemas.Token(**res.json())
    payload = jwt.decode(login_res.access_token,
                         settings.secret_key, algorithms=[settings.algorithm])
    id = payload.get("user_id")
    assert id == test_user['id']
    assert login_res.token_type == "bearer"
    assert res.status_code == 200

@pytest.mark.parametrize("email, password, status_code", [('wrong@gmail.com', 'password123', 403), ('test@gmail.com', '32423', 403), ('wrong@gmail.com', 'psf23432', 403), (None, 'test123', 422), ('test@gmail.com', None, 422)])
def test_incorrect_login(client, email, password, status_code):
    res = client.post("/login", data={"username": email, "password": password})

    assert res.status_code == status_code