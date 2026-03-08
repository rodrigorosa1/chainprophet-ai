def test_create_user_route(client, fake_user_payload):
    response = client.post("users/", json=fake_user_payload)
    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert "phone" in data

    assert data["name"] == fake_user_payload["name"]
    assert data["email"] == fake_user_payload["email"]
    assert data["phone"] == fake_user_payload["phone"]


def test_get_user_route(client, fake_user_payload, fake_auth_payload):
    create_response = client.post("users/", json=fake_user_payload)
    assert create_response.status_code == 200

    created_user = create_response.json()
    user_id = created_user["id"]

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    get_response = client.get(
        f"users/{user_id}",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
    )
    assert get_response.status_code == 200

    retrieved_user = get_response.json()
    assert retrieved_user["id"] == user_id
    assert retrieved_user["name"] == fake_user_payload["name"]
    assert retrieved_user["email"] == fake_user_payload["email"]
    assert retrieved_user["phone"] == fake_user_payload["phone"]


def test_list_users_route(client, fake_user_payload, fake_auth_payload):
    create_response = client.post("/users/", json=fake_user_payload)
    assert create_response.status_code == 200

    created_user = create_response.json()
    user_id = created_user["id"]

    auth_response = client.post("/auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    list_response = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
    )

    assert list_response.status_code == 200

    users = list_response.json()

    assert isinstance(users, list)
    assert len(users) > 0

    found_user = next((u for u in users if u["id"] == user_id), None)

    assert found_user is not None
    assert found_user["name"] == fake_user_payload["name"]
    assert found_user["email"] == fake_user_payload["email"]
    assert found_user["phone"] == fake_user_payload["phone"]


def test_update_user_route(client, fake_user_payload, fake_auth_payload):
    create_response = client.post("/users/", json=fake_user_payload)
    assert create_response.status_code == 200

    created_user = create_response.json()
    user_id = created_user["id"]

    auth_response = client.post("/auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    update_response = client.patch(
        f"/users/{user_id}",
        json=fake_user_payload,
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
    )

    assert update_response.status_code == 200

    updated_user = update_response.json()
    assert updated_user["id"] == user_id
    assert updated_user["name"] == fake_user_payload["name"]
    assert updated_user["email"] == fake_user_payload["email"]
    assert updated_user["phone"] == fake_user_payload["phone"]
