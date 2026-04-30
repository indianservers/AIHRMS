import pytest
from fastapi.testclient import TestClient
from app.core.security import get_password_hash
from app.models.user import User, Role


def test_login_success(client, db):
    role = Role(name="employee_role", description="Employee", is_system=False)
    db.add(role)
    db.flush()
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("Test@123456"),
        is_active=True,
        role_id=role.id,
    )
    db.add(user)
    db.commit()

    response = client.post("/api/v1/auth/login", json={
        "email": "test@example.com",
        "password": "Test@123456",
    })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["email"] == "test@example.com"


def test_login_wrong_password(client, db):
    role = Role(name="employee_role2", description="Employee", is_system=False)
    db.add(role)
    db.flush()
    user = User(
        email="test2@example.com",
        hashed_password=get_password_hash("Test@123456"),
        is_active=True,
        role_id=role.id,
    )
    db.add(user)
    db.commit()

    response = client.post("/api/v1/auth/login", json={
        "email": "test2@example.com",
        "password": "WrongPassword",
    })
    assert response.status_code == 401


def test_login_nonexistent_user(client):
    response = client.post("/api/v1/auth/login", json={
        "email": "nobody@example.com",
        "password": "Test@123456",
    })
    assert response.status_code == 401


def test_get_me(client, superuser_headers):
    response = client.get("/api/v1/auth/me", headers=superuser_headers)
    assert response.status_code == 200
    data = response.json()
    assert "email" in data
    assert data["is_superuser"] is True


def test_get_me_unauthorized(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403  # Missing bearer token


def test_refresh_token(client, db):
    role = Role(name="refresh_role", description="Role", is_system=False)
    db.add(role)
    db.flush()
    user = User(
        email="refresh@example.com",
        hashed_password=get_password_hash("Refresh@123"),
        is_active=True,
        role_id=role.id,
    )
    db.add(user)
    db.commit()

    login_response = client.post("/api/v1/auth/login", json={
        "email": "refresh@example.com",
        "password": "Refresh@123",
    })
    refresh_token = login_response.json()["refresh_token"]

    refresh_response = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_response.status_code == 200
    assert "access_token" in refresh_response.json()


def test_change_password(client, db):
    role = Role(name="change_pw_role", description="Role", is_system=False)
    db.add(role)
    db.flush()
    user = User(
        email="changepw@example.com",
        hashed_password=get_password_hash("OldPass@123"),
        is_active=True,
        role_id=role.id,
    )
    db.add(user)
    db.commit()

    login_response = client.post("/api/v1/auth/login", json={
        "email": "changepw@example.com",
        "password": "OldPass@123",
    })
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.post("/api/v1/auth/change-password", json={
        "current_password": "OldPass@123",
        "new_password": "NewPass@456",
    }, headers=headers)
    assert response.status_code == 200

    # Old password should no longer work
    response2 = client.post("/api/v1/auth/login", json={
        "email": "changepw@example.com",
        "password": "OldPass@123",
    })
    assert response2.status_code == 401
