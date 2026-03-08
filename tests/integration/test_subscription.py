def test_create_subscription_route(
    client,
    fake_auth_payload,
    fake_user_payload,
    fake_plan_payload,
    fake_subscription_payload,
):
    user_response = client.post("users/", json=fake_user_payload)
    assert user_response.status_code == 200

    user = user_response.json()

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    plan_response = client.post(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=fake_plan_payload,
    )
    assert plan_response.status_code == 200
    plan = plan_response.json()

    subscription_payload = fake_subscription_payload(
        plan_id=plan["id"], user_id=user["id"]
    )

    response = client.post(
        "subscriptions/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=subscription_payload,
    )
    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "user_id" in data
    assert "plan_id" in data
    assert "active" in data
    assert "started_at" in data
    assert "canceled_at" in data

    assert data["user_id"] == subscription_payload["user_id"]
    assert data["plan_id"] == subscription_payload["plan_id"]
    assert data["active"] == subscription_payload["active"]


def test_get_subscription_route(
    client,
    fake_auth_payload,
    fake_user_payload,
    fake_plan_payload,
    fake_subscription_payload,
):
    user_response = client.post("users/", json=fake_user_payload)
    assert user_response.status_code == 200

    user = user_response.json()

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    plan_response = client.post(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=fake_plan_payload,
    )
    assert plan_response.status_code == 200
    plan = plan_response.json()

    subscription_payload = fake_subscription_payload(
        plan_id=plan["id"], user_id=user["id"]
    )

    subscription_response = client.post(
        "subscriptions/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=subscription_payload,
    )
    assert subscription_response.status_code == 200
    subscription = subscription_response.json()
    subscription_id = subscription["id"]

    get_response = client.get(
        f"subscriptions/{subscription_id}",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
    )
    assert get_response.status_code == 200

    retrieved_subscription = get_response.json()
    assert retrieved_subscription["id"] == subscription_id
    assert retrieved_subscription["user_id"] == subscription_payload["user_id"]
    assert retrieved_subscription["plan_id"] == subscription_payload["plan_id"]
    assert retrieved_subscription["active"] == subscription_payload["active"]


def test_list_subscriptions_route(
    client,
    fake_auth_payload,
    fake_user_payload,
    fake_plan_payload,
    fake_subscription_payload,
):
    user_response = client.post("users/", json=fake_user_payload)
    assert user_response.status_code == 200

    user = user_response.json()

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    plan_response = client.post(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=fake_plan_payload,
    )
    assert plan_response.status_code == 200
    plan = plan_response.json()

    subscription_payload = fake_subscription_payload(
        plan_id=plan["id"], user_id=user["id"]
    )

    subscription_response = client.post(
        "subscriptions/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=subscription_payload,
    )
    assert subscription_response.status_code == 200

    list_response = client.get(
        "subscriptions/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
    )
    assert list_response.status_code == 200

    subscriptions = list_response.json()
    assert isinstance(subscriptions, list)
    assert len(subscriptions) > 0


def test_update_subscription_route(
    client,
    fake_auth_payload,
    fake_user_payload,
    fake_plan_payload,
    fake_subscription_payload,
):
    user_response = client.post("users/", json=fake_user_payload)
    assert user_response.status_code == 200

    user = user_response.json()

    auth_response = client.post("auth/login", json=fake_auth_payload)
    assert auth_response.status_code == 200
    auth_response_data = auth_response.json()

    plan_response = client.post(
        "plans/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=fake_plan_payload,
    )
    assert plan_response.status_code == 200
    plan = plan_response.json()

    subscription_payload = fake_subscription_payload(
        plan_id=plan["id"], user_id=user["id"]
    )

    subscription_response = client.post(
        "subscriptions/",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=subscription_payload,
    )
    assert subscription_response.status_code == 200
    subscription = subscription_response.json()
    subscription_id = subscription["id"]

    update_data = {
        "plan_id": plan["id"],
        "user_id": user["id"],
        "active": False,
    }

    update_response = client.patch(
        f"subscriptions/{subscription_id}",
        headers={"Authorization": f"Bearer {auth_response_data['access_token']}"},
        json=update_data,
    )
    assert update_response.status_code == 200

    updated_subscription = update_response.json()
    assert updated_subscription["id"] == subscription_id
    assert updated_subscription["active"] == update_data["active"]
