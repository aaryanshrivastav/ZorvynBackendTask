def test_login_refresh_logout_flow(client):
    login = client.post("/auth/login", json={"username": "analyst", "password": "analyst123"})
    assert login.status_code == 200
    body = login.json()
    assert body["access_token"]
    assert body["refresh_token"]

    refresh = client.post("/auth/refresh", json={"refresh_token": body["refresh_token"]})
    assert refresh.status_code == 200

    logout = client.post(
        "/auth/logout",
        json={"refresh_token": refresh.json()["refresh_token"]},
        headers={"Authorization": f"Bearer {refresh.json()['access_token']}"},
    )
    assert logout.status_code == 200


def test_admin_only_user_creation(client, analyst_token, admin_token):
    forbidden = client.post(
        "/admin/users",
        json={"username": "x1", "password": "x1", "role": "Viewer"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert forbidden.status_code == 403

    allowed = client.post(
        "/admin/users",
        json={"username": "newviewer", "password": "pass123", "role": "Viewer"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert allowed.status_code == 200
