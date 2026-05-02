def test_notification_inbox_and_delivery_hooks(client, superuser_headers):
    me = client.get("/api/v1/auth/me", headers=superuser_headers)
    assert me.status_code == 200
    user_id = me.json()["id"]

    create = client.post("/api/v1/notifications/", json={
        "user_id": user_id,
        "title": "Leave request approved",
        "message": "Your leave request was approved by HR.",
        "module": "leave",
        "event_type": "leave_approved",
        "action_url": "/leave",
        "channels": ["in_app", "email", "sms"],
    }, headers=superuser_headers)
    assert create.status_code == 201
    assert {log["channel"] for log in create.json()["delivery_logs"]} == {"in_app", "email", "sms"}

    count = client.get("/api/v1/notifications/unread-count", headers=superuser_headers)
    assert count.status_code == 200
    assert count.json()["unread"] == 1

    inbox = client.get("/api/v1/notifications/", headers=superuser_headers)
    assert inbox.status_code == 200
    assert inbox.json()["items"][0]["title"] == "Leave request approved"

    mark_read = client.put(f"/api/v1/notifications/{create.json()['id']}/read", headers=superuser_headers)
    assert mark_read.status_code == 200
    assert mark_read.json()["is_read"] is True

    count_after = client.get("/api/v1/notifications/unread-count", headers=superuser_headers)
    assert count_after.json()["unread"] == 0
