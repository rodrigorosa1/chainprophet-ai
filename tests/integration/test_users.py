from app.constants.enums.type_notification_enum import TypeNotificationEnum


def test_create_user_route(client):
    payload = {
        "name": "Anakin Skywalker",
        "email": "anakin.skywalker@jedi.com",
        "password": "123",
        "phone": "55489848999",
        "type_notification": "ALL",
    }

    response = client.post("users/register", json=payload)
    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert "name" in data
    assert "email" in data
    assert "phone" in data
    assert "type_notification" in data

    assert data["name"] == payload["name"]
    assert data["email"] == payload["email"]
    assert data["phone"] == payload["phone"]
    assert data["type_notification"] == payload["type_notification"]
