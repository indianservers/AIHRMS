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
