def _register_and_login(client, email, name="User"):
    client.post(
        "/api/auth/register",
        json={"email": email, "password": "PolarisPass1!", "name": name},
    )
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "PolarisPass1!"},
    )
    return response.json()["data"]["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def test_create_and_get_org(client):
    token = _register_and_login(client, "crud@example.com", "Crud")
    created = client.post("/api/orgs", json={"name": "Crud Org"}, headers=_auth_header(token))
    assert created.status_code == 200
    org_id = created.json()["data"]["id"]
    fetched = client.get(f"/api/orgs/{org_id}", headers=_auth_header(token))
    assert fetched.status_code == 200
    assert fetched.json()["data"]["name"] == "Crud Org"


def test_create_project_and_service(client):
    token = _register_and_login(client, "crud2@example.com", "Crud2")
    org_id = client.post("/api/orgs", json={"name": "Crud Org"}, headers=_auth_header(token)).json()["data"]["id"]
    project_id = client.post(
        f"/api/orgs/{org_id}/projects",
        json={"name": "Web Console", "key": "WEB"},
        headers=_auth_header(token),
    ).json()["data"]["id"]
    service_created = client.post(
        f"/api/projects/{project_id}/services",
        json={"name": "Console API", "type": "API", "environment": "PROD"},
        headers=_auth_header(token),
    )
    assert service_created.status_code == 200
    service_id = service_created.json()["data"]["id"]
    fetched = client.get(f"/api/services/{service_id}", headers=_auth_header(token))
    assert fetched.status_code == 200
