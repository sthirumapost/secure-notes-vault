def register_and_login(client, username, password):
    client.post("/auth/register", json={"username": username, "password": password})
    r = client.post("/auth/login", json={"username": username, "password": password})
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_user_cannot_access_another_users_note(client):
    alice_headers = register_and_login(client, "alice2", "secret123")
    bob_headers = register_and_login(client, "bob2", "secret123")

    note_resp = client.post("/notes", json={"content": "alice private note"}, headers=alice_headers)
    assert note_resp.status_code == 201
    note_id = note_resp.json()["id"]

    forbidden = client.get(f"/notes/{note_id}", headers=bob_headers)
    assert forbidden.status_code == 403


def test_shared_note_is_read_only(client):
    alice_headers = register_and_login(client, "alice3", "secret123")
    bob_headers = register_and_login(client, "bob3", "secret123")

    note_resp = client.post("/notes", json={"content": "shared note"}, headers=alice_headers)
    note_id = note_resp.json()["id"]

    share_resp = client.post(f"/notes/{note_id}/share", json={"username": "bob3"}, headers=alice_headers)
    assert share_resp.status_code == 200

    read_resp = client.get(f"/notes/{note_id}", headers=bob_headers)
    assert read_resp.status_code == 200
    assert read_resp.json()["access"] == "read"

    update_resp = client.put(f"/notes/{note_id}", json={"content": "bob edit attempt"}, headers=bob_headers)
    assert update_resp.status_code == 403


def test_owner_crud_flow(client):
    headers = register_and_login(client, "carol", "secret123")

    create_resp = client.post("/notes", json={"content": "first note"}, headers=headers)
    assert create_resp.status_code == 201
    note_id = create_resp.json()["id"]

    list_resp = client.get("/notes", headers=headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    update_resp = client.put(f"/notes/{note_id}", json={"content": "updated note"}, headers=headers)
    assert update_resp.status_code == 200
    assert update_resp.json()["content"] == "updated note"

    delete_resp = client.delete(f"/notes/{note_id}", headers=headers)
    assert delete_resp.status_code == 200
