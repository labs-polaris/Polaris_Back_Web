def test_register(client):
    response = client.post(
        "/api/auth/register",
        json={"email": "user@example.com", "password": "PolarisPass1!", "name": "User"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["ok"] is True
    assert body["data"]["email"] == "user@example.com"


def test_login(client):
    client.post(
        "/api/auth/register",
        json={"email": "login@example.com", "password": "PolarisPass1!", "name": "Login"},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "login@example.com", "password": "PolarisPass1!"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["access_token"]
    assert body["data"]["refresh_token"]


def test_refresh(client):
    client.post(
        "/api/auth/register",
        json={"email": "refresh@example.com", "password": "PolarisPass1!", "name": "Refresh"},
    )
    login = client.post(
        "/api/auth/login",
        json={"email": "refresh@example.com", "password": "PolarisPass1!"},
    )
    refresh_token = login.json()["data"]["refresh_token"]
    response = client.post("/api/auth/refresh", json={"refresh_token": refresh_token})
    assert response.status_code == 200
    body = response.json()
    assert body["data"]["access_token"]
