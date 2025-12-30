def _register(client, email, name="User"):
    return client.post(
        "/api/auth/register",
        json={"email": email, "password": "PolarisPass1!", "name": name},
    )


def _login(client, email):
    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "PolarisPass1!"},
    )
    return response.json()["data"]["access_token"]


def _auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def _create_org(client, token, name="Polaris Lab Org"):
    response = client.post("/api/orgs", json={"name": name}, headers=_auth_header(token))
    return response.json()["data"]["id"]


def _add_member(client, token, org_id, email, role):
    return client.post(
        f"/api/orgs/{org_id}/members",
        json={"email": email, "role": role},
        headers=_auth_header(token),
    )


def test_owner_can_create_project(client):
    _register(client, "owner@example.com", "Owner")
    owner_token = _login(client, "owner@example.com")
    org_id = _create_org(client, owner_token)
    response = client.post(
        f"/api/orgs/{org_id}/projects",
        json={"name": "Web Console", "key": "WEB"},
        headers=_auth_header(owner_token),
    )
    assert response.status_code == 200


def test_admin_can_create_service(client):
    _register(client, "owner2@example.com", "Owner2")
    _register(client, "admin@example.com", "Admin")
    owner_token = _login(client, "owner2@example.com")
    admin_token = _login(client, "admin@example.com")
    org_id = _create_org(client, owner_token)
    _add_member(client, owner_token, org_id, "admin@example.com", "admin")
    project = client.post(
        f"/api/orgs/{org_id}/projects",
        json={"name": "Web Console", "key": "WEB"},
        headers=_auth_header(owner_token),
    ).json()["data"]["id"]
    response = client.post(
        f"/api/projects/{project}/services",
        json={"name": "Console API", "type": "API", "environment": "PROD"},
        headers=_auth_header(admin_token),
    )
    assert response.status_code == 200


def test_member_cannot_create_project(client):
    _register(client, "owner3@example.com", "Owner3")
    _register(client, "member@example.com", "Member")
    owner_token = _login(client, "owner3@example.com")
    member_token = _login(client, "member@example.com")
    org_id = _create_org(client, owner_token)
    _add_member(client, owner_token, org_id, "member@example.com", "member")
    response = client.post(
        f"/api/orgs/{org_id}/projects",
        json={"name": "Forbidden", "key": "NOPE"},
        headers=_auth_header(member_token),
    )
    assert response.status_code == 403
