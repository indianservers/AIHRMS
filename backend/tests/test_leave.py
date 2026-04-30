import pytest
from datetime import date, timedelta
from decimal import Decimal


def _create_employee_with_leave(db, client, headers):
    """Helper to create an employee with leave balance."""
    from app.models.employee import Employee
    from app.models.leave import LeaveType, LeaveBalance
    from app.models.user import User, Role
    from app.core.security import get_password_hash

    role = Role(name=f"emp_role_{id(db)}", description="Employee", is_system=False)
    db.add(role)
    db.flush()

    user = User(
        email=f"leavetest_{id(db)}@test.com",
        hashed_password=get_password_hash("Test@123"),
        is_active=True,
        role_id=role.id,
    )
    db.add(user)
    db.flush()

    emp = Employee(
        employee_id=f"LEAVEEMP{id(db)}",
        first_name="Leave",
        last_name="Tester",
        date_of_joining=date(2023, 1, 1),
        user_id=user.id,
    )
    db.add(emp)
    db.flush()

    lt = LeaveType(
        name="Annual Leave",
        code=f"AL{id(db)}",
        days_allowed=Decimal("21"),
        carry_forward=False,
    )
    db.add(lt)
    db.flush()

    balance = LeaveBalance(
        employee_id=emp.id,
        leave_type_id=lt.id,
        year=date.today().year,
        allocated=Decimal("21"),
        used=Decimal("0"),
        pending=Decimal("0"),
    )
    db.add(balance)
    db.commit()

    return emp, lt, user


def test_list_leave_types(client, superuser_headers):
    response = client.get("/api/v1/leave/types", headers=superuser_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_leave_type(client, superuser_headers):
    response = client.post("/api/v1/leave/types", json={
        "name": "Sick Leave",
        "code": "SL001",
        "days_allowed": 10,
        "carry_forward": False,
    }, headers=superuser_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Sick Leave"
    assert data["code"] == "SL001"


def test_leave_balance_check(client, db):
    from app.models.user import User
    from app.core.security import get_password_hash

    emp, lt, user = _create_employee_with_leave(db, client, {})

    login_response = client.post("/api/v1/auth/login", json={
        "email": user.email,
        "password": "Test@123",
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    response = client.get("/api/v1/leave/balance", headers=headers)
    assert response.status_code == 200
    balances = response.json()
    assert len(balances) > 0


def test_leave_request_workflow(client, db):
    """Test apply → approve flow."""
    from app.models.user import User, Role
    from app.core.security import get_password_hash

    emp, lt, user = _create_employee_with_leave(db, client, {})

    login_resp = client.post("/api/v1/auth/login", json={"email": user.email, "password": "Test@123"})
    emp_token = login_resp.json()["access_token"]
    emp_headers = {"Authorization": f"Bearer {emp_token}"}

    # Apply for leave
    from_date = (date.today() + timedelta(days=7)).isoformat()
    to_date = (date.today() + timedelta(days=9)).isoformat()
    apply_resp = client.post("/api/v1/leave/apply", json={
        "leave_type_id": lt.id,
        "from_date": from_date,
        "to_date": to_date,
        "reason": "Family vacation",
    }, headers=emp_headers)
    assert apply_resp.status_code == 201
    request_id = apply_resp.json()["id"]
    assert apply_resp.json()["status"] == "Pending"
