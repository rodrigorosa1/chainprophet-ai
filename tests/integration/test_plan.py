def test_create_plan_route(
    client, fake_plan_payload, fake_user_payload, fake_auth_payload
):
    create_response = client.post("users/", json=fake_user_payload)
    assert create_response.status_code == 200

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    response = client.post(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=fake_plan_payload,
    )
    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "name" in data
    assert "daily_amount" in data
    assert "no_limit" in data
    assert "value" in data

    assert data["name"] == fake_plan_payload["name"]
    assert data["daily_amount"] == fake_plan_payload["daily_amount"]
    assert data["no_limit"] == fake_plan_payload["no_limit"]
    assert data["value"] == fake_plan_payload["value"]


def test_get_plan_route(
    client, fake_plan_payload, fake_user_payload, fake_auth_payload
):
    create_response = client.post("users/", json=fake_user_payload)
    assert create_response.status_code == 200

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    response = client.post(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=fake_plan_payload,
    )
    assert response.status_code == 200

    created_plan = response.json()
    plan_id = created_plan["id"]

    get_response = client.get(
        f"plans/{plan_id}",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
    )
    assert get_response.status_code == 200

    retrieved_plan = get_response.json()
    assert retrieved_plan["id"] == plan_id
    assert retrieved_plan["name"] == fake_plan_payload["name"]
    assert retrieved_plan["daily_amount"] == fake_plan_payload["daily_amount"]
    assert retrieved_plan["no_limit"] == fake_plan_payload["no_limit"]
    assert retrieved_plan["value"] == fake_plan_payload["value"]


def test_list_plans_route(
    client, fake_plan_payload, fake_user_payload, fake_auth_payload
):
    create_response = client.post("users/", json=fake_user_payload)
    assert create_response.status_code == 200

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    response = client.post(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=fake_plan_payload,
    )
    assert response.status_code == 200

    created_plan = response.json()
    plan_id = created_plan["id"]

    list_response = client.get(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
    )
    assert list_response.status_code == 200

    plans = list_response.json()
    assert len(plans) > 0
    assert isinstance(plans, list)

    found_plan = next((plan for plan in plans if plan["id"] == plan_id), None)

    assert found_plan is not None
    assert found_plan["name"] == fake_plan_payload["name"]
    assert found_plan["daily_amount"] == fake_plan_payload["daily_amount"]
    assert found_plan["no_limit"] == fake_plan_payload["no_limit"]
    assert found_plan["value"] == fake_plan_payload["value"]


def test_update_plan_route(
    client, fake_plan_payload, fake_user_payload, fake_auth_payload
):
    create_response = client.post("users/", json=fake_user_payload)
    assert create_response.status_code == 200

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    response = client.post(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=fake_plan_payload,
    )
    assert response.status_code == 200

    created_plan = response.json()
    plan_id = created_plan["id"]

    updated_payload = {
        "name": "Updated Plan",
        "daily_amount": 20,
        "no_limit": True,
        "value": 19.99,
    }

    update_response = client.patch(
        f"plans/{plan_id}",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=updated_payload,
    )
    assert update_response.status_code == 200

    updated_plan = update_response.json()
    assert updated_plan["id"] == plan_id
    assert updated_plan["name"] == updated_payload["name"]
    assert updated_plan["daily_amount"] == updated_payload["daily_amount"]
    assert updated_plan["no_limit"] == updated_payload["no_limit"]
    assert updated_plan["value"] == updated_payload["value"]
