def test_register_and_login(client):
    r = client.post("/auth/register", json={"username": "alice", "password": "secret123"})
    assert r.status_code == 201
    assert r.json()["message"] == "User registered successfully"

    r = client.post("/auth/login", json={"username": "alice", "password": "secret123"})
    assert r.status_code == 200
    assert "access_token" in r.json()


def test_login_with_wrong_password_fails(client):
    client.post("/auth/register", json={"username": "alice", "password": "secret123"})
    r = client.post("/auth/login", json={"username": "alice", "password": "wrongpass"})
    assert r.status_code == 401
