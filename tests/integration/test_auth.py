def test_auth_route(client, fake_auth_payload, fake_user_payload):

    create_response = client.post("users/", json=fake_user_payload)
    assert create_response.status_code == 200

    response = client.post("auth/login", json=fake_auth_payload)
    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
