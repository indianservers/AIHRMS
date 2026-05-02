import pytest
from datetime import date


def test_list_employees(client, superuser_headers):
    response = client.get("/api/v1/employees/", headers=superuser_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data


def test_create_employee(client, superuser_headers, db):
    from app.models.company import Branch, Department, Designation, Company

    # Create company structure
    company = Company(name="Test Corp")
    db.add(company)
    db.flush()
    branch = Branch(name="HQ", company_id=company.id)
    db.add(branch)
    db.flush()
    dept = Department(name="Engineering", branch_id=branch.id)
    db.add(dept)
    db.flush()
    desig = Designation(name="Engineer", department_id=dept.id)
    db.add(desig)
    db.commit()

    response = client.post("/api/v1/employees/", json={
        "first_name": "John",
        "last_name": "Doe",
        "date_of_joining": str(date.today()),
        "employment_type": "Full-time",
        "branch_id": branch.id,
        "department_id": dept.id,
        "designation_id": desig.id,
        "create_user_account": False,
    }, headers=superuser_headers)
    assert response.status_code == 201
    data = response.json()
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "employee_id" in data


def test_get_employee(client, superuser_headers, db):
    from app.models.employee import Employee
    from app.models.company import Designation

    emp = Employee(
        employee_id="EMP99999",
        first_name="Jane",
        last_name="Smith",
        date_of_joining=date.today(),
    )
    db.add(emp)
    db.commit()

    response = client.get(f"/api/v1/employees/{emp.id}", headers=superuser_headers)
    assert response.status_code == 200
    assert response.json()["first_name"] == "Jane"


def test_update_employee(client, superuser_headers, db):
    from app.models.employee import Employee

    emp = Employee(
        employee_id="EMP88888",
        first_name="Alice",
        last_name="Brown",
        date_of_joining=date.today(),
    )
    db.add(emp)
    db.commit()

    response = client.put(f"/api/v1/employees/{emp.id}", json={
        "phone_number": "+91-9876543210",
        "marital_status": "Single",
    }, headers=superuser_headers)
    assert response.status_code == 200
    assert response.json()["phone_number"] == "+91-9876543210"


def test_get_employee_stats(client, superuser_headers):
    response = client.get("/api/v1/employees/stats", headers=superuser_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "active" in data


def test_employee_not_found(client, superuser_headers):
    response = client.get("/api/v1/employees/999999", headers=superuser_headers)
    assert response.status_code == 404


def test_employee_csv_import_export_with_row_errors(client, superuser_headers):
    csv_body = (
        "employee_id,first_name,last_name,date_of_joining,personal_email,phone_number\n"
        "BULK001,Bulk,Good,2024-01-15,bulk.good@test.com,9999999999\n"
        "BULK002,,Missing,2024-01-16,missing@test.com,8888888888\n"
        "BULK003,Bad,Date,15-01-2024,bad.date@test.com,7777777777\n"
    )

    response = client.post(
        "/api/v1/employees/import",
        files={"file": ("employees.csv", csv_body, "text/csv")},
        headers=superuser_headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["created"] == 1
    assert data["failed"] == 2
    assert data["errors"][0]["row"] == 3

    exported = client.get("/api/v1/employees/export", headers=superuser_headers)
    assert exported.status_code == 200
    assert "BULK001" in exported.text
    assert "bulk.good@test.com" in exported.text


def test_create_employee_lifecycle_event(client, superuser_headers, db):
    from app.models.employee import Employee

    emp = Employee(
        employee_id="EMP77777",
        first_name="Ravi",
        last_name="Kumar",
        date_of_joining=date.today(),
        status="Probation",
    )
    db.add(emp)
    db.commit()

    response = client.post(
        f"/api/v1/employees/{emp.id}/lifecycle",
        json={
            "event_type": "confirmation",
            "event_date": str(date.today()),
            "to_status": "Active",
            "reason": "Probation completed",
        },
        headers=superuser_headers,
    )

    assert response.status_code == 201
    data = response.json()
    assert data["event_type"] == "confirmation"
    assert data["from_status"] == "Probation"
    assert data["to_status"] == "Active"
    assert data["employee_id"] == emp.id


def test_lifecycle_event_can_apply_employee_changes(client, superuser_headers, db):
    from app.models.employee import Employee

    emp = Employee(
        employee_id="EMP66666",
        first_name="Meera",
        last_name="Shah",
        date_of_joining=date.today(),
        status="Probation",
    )
    db.add(emp)
    db.commit()

    response = client.post(
        f"/api/v1/employees/{emp.id}/lifecycle",
        json={
            "event_type": "confirmation",
            "event_date": str(date.today()),
            "to_status": "Active",
            "apply_to_employee": True,
        },
        headers=superuser_headers,
    )

    assert response.status_code == 201
    db.refresh(emp)
    assert emp.status == "Active"

    history = client.get(f"/api/v1/employees/{emp.id}/lifecycle", headers=superuser_headers)
    assert history.status_code == 200
    assert len(history.json()) == 1
    assert history.json()[0]["from_status"] == "Probation"


def test_hr_cannot_create_employee_login_account(client, db):
    from app.db.init_db import init_db

    init_db(db)
    login = client.post("/api/v1/auth/login", json={
        "email": "hr@aihrms.com",
        "password": "HR@123456",
    })
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    response = client.post("/api/v1/employees/", json={
        "first_name": "Login",
        "last_name": "Blocked",
        "date_of_joining": str(date.today()),
        "create_user_account": True,
        "user_email": "blocked.employee@aihrms.com",
        "user_password": "Employee@123456",
    }, headers=headers)
    assert response.status_code == 403
    assert "only admin" in response.json()["detail"].lower()
