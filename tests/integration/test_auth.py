def test_auth_route(client, fake_auth_payload, fake_user_payload):

    create_response = client.post("users/", json=fake_user_payload)
    assert create_response.status_code == 200

    response = client.post("auth/login", json=fake_auth_payload)
    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data


def test_register_route(
    client,
    fake_auth_payload,
    fake_user_payload,
    fake_trial_plan_payload,
    fake_register_payload,
):
    create_response = client.post("users/", json=fake_user_payload)
    assert create_response.status_code == 200

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    plan = client.post(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=fake_trial_plan_payload,
    )
    assert plan.status_code == 200

    response = client.post("auth/register", json=fake_register_payload)
    assert response.status_code == 200

    data = response.json()

    assert response.status_code == 200

    assert "id" in data
