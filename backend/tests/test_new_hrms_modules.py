from decimal import Decimal
from app.db.init_db import init_db
from app.models.employee import Employee
from app.models.leave import LeaveBalance, LeaveType
from app.models.payroll import PayrollRecord, PayrollRun


def _login(client, email, password):
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_whatsapp_ess_benefits_statutory_and_bgv_modules_work(client, db):
    init_db(db)
    admin = _login(client, "admin@aihrms.com", "Admin@123456")
    employee = db.query(Employee).filter(Employee.employee_id == "DEMO-EMP-001").first()
    employee.phone_number = "9999999999"
    leave_type = db.query(LeaveType).filter(LeaveType.code == "CL").first()
    db.add(LeaveBalance(employee_id=employee.id, leave_type_id=leave_type.id, year=2026, allocated=12, used=2, pending=0, carried_forward=0))
    run = PayrollRun(month=4, year=2026, status="Approved")
    db.add(run)
    db.flush()
    db.add(PayrollRecord(payroll_run_id=run.id, employee_id=employee.id, gross_salary=Decimal("50000"), total_deductions=Decimal("5000"), net_salary=Decimal("45000")))
    db.commit()

    wa_config = client.post(
        "/api/v1/whatsapp-ess/configs",
        json={"business_phone_number": "919000000000", "webhook_url": "https://example.com/whatsapp"},
        headers=admin,
    )
    assert wa_config.status_code == 201
    inbound = client.post(
        "/api/v1/whatsapp-ess/messages/inbound",
        json={"phone_number": "9999999999", "message_text": "show my leave balance"},
        headers=admin,
    )
    assert inbound.status_code == 201
    assert inbound.json()["intent"] == "leave_balance"
    assert "CL" in inbound.json()["response_text"]

    legal_entity = client.post(
        "/api/v1/statutory-compliance/legal-entities",
        json={
            "legal_name": "AI HRMS Private Limited",
            "pan": "ABCDE1234F",
            "tan": "HYDA12345B",
            "pf_establishment_code": "APHYD1234567",
            "esi_employer_code": "52001234560001099",
            "is_default": True,
        },
        headers=admin,
    )
    assert legal_entity.status_code == 201
    legal_entity_id = legal_entity.json()["id"]

    form16 = client.post(
        "/api/v1/statutory-compliance/form16",
        json={"legal_entity_id": legal_entity_id, "employee_id": employee.id, "financial_year": "2025-26", "taxable_income": "600000", "tax_deducted": "25000"},
        headers=admin,
    )
    assert form16.status_code == 201
    published = client.put(
        f"/api/v1/statutory-compliance/form16/{form16.json()['id']}/publish",
        json={"combined_pdf_url": "/uploads/form16/demo.pdf"},
        headers=admin,
    )
    assert published.status_code == 200
    assert published.json()["status"] == "Published"

    tds = client.post(
        "/api/v1/statutory-compliance/tds-filings",
        json={"legal_entity_id": legal_entity_id, "financial_year": "2025-26", "quarter": "Q4", "form_type": "24Q", "total_tax_deducted": "25000"},
        headers=admin,
    )
    assert tds.status_code == 201
    filed = client.put(
        f"/api/v1/statutory-compliance/tds-filings/{tds.json()['id']}/submit",
        json={"return_file_url": "/uploads/tds/24q.csv", "acknowledgement_number": "TDS-ACK-1"},
        headers=admin,
    )
    assert filed.status_code == 200
    assert filed.json()["status"] == "Filed"

    epfo = client.post(
        "/api/v1/statutory-compliance/portal-submissions",
        json={"legal_entity_id": legal_entity_id, "portal_type": "EPFO", "period_month": 4, "period_year": 2026, "submission_type": "ECR", "total_amount": "12000"},
        headers=admin,
    )
    assert epfo.status_code == 201
    submitted = client.put(
        f"/api/v1/statutory-compliance/portal-submissions/{epfo.json()['id']}/submit",
        json={"acknowledgement_number": "EPFO-ACK-1", "payment_reference": "UTR123"},
        headers=admin,
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "Submitted"

    event = client.post(
        "/api/v1/statutory-compliance/calendar",
        json={"legal_entity_id": legal_entity_id, "compliance_type": "TDS", "financial_year": "2025-26", "due_date": "2026-05-31"},
        headers=admin,
    )
    assert event.status_code == 201
    completed = client.put(f"/api/v1/statutory-compliance/calendar/{event.json()['id']}", json={"status": "Completed"}, headers=admin)
    assert completed.status_code == 200
    assert completed.json()["completed_at"] is not None

    plan = client.post(
        "/api/v1/benefits/plans",
        json={"name": "Group Health Gold", "plan_type": "Group Health", "provider_name": "Demo Insurer", "employee_contribution": "500", "employer_contribution": "1500"},
        headers=admin,
    )
    assert plan.status_code == 201
    enrollment = client.post(
        "/api/v1/benefits/enrollments",
        json={"employee_id": employee.id, "benefit_plan_id": plan.json()["id"], "coverage_level": "Family", "start_date": "2026-04-01", "employee_contribution": "500", "employer_contribution": "1500"},
        headers=admin,
    )
    assert enrollment.status_code == 201
    deduction = client.post(
        "/api/v1/benefits/payroll-deductions",
        json={"enrollment_id": enrollment.json()["id"], "month": 4, "year": 2026},
        headers=admin,
    )
    assert deduction.status_code == 201
    assert deduction.json()["employee_amount"] == "500.00"

    flexi = client.post(
        "/api/v1/benefits/flexi-policies",
        json={"name": "Meal Card", "component_code": "MEAL", "monthly_limit": "2200", "annual_limit": "26400"},
        headers=admin,
    )
    assert flexi.status_code == 201
    allocation = client.post(
        "/api/v1/benefits/flexi-allocations",
        json={"employee_id": employee.id, "policy_id": flexi.json()["id"], "financial_year": "2025-26", "allocated_amount": "24000", "claimed_amount": "10000"},
        headers=admin,
    )
    assert allocation.status_code == 201
    assert allocation.json()["taxable_fallback_amount"] == "14000.00"

    vendor = client.post(
        "/api/v1/background-verification/vendors",
        json={"name": "Demo BGV Vendor", "contact_email": "ops@bgv.example"},
        headers=admin,
    )
    assert vendor.status_code == 201
    bgv = client.post(
        "/api/v1/background-verification/requests",
        json={
            "vendor_id": vendor.json()["id"],
            "employee_id": employee.id,
            "package_name": "Standard Employee",
            "checks": [{"check_type": "Identity"}, {"check_type": "Employment"}],
        },
        headers=admin,
    )
    assert bgv.status_code == 201
    check_id = bgv.json()["checks"][0]["id"]
    updated = client.put(
        f"/api/v1/background-verification/checks/{check_id}",
        json={"status": "Completed", "result": "Clear", "verified_by": "Demo Vendor"},
        headers=admin,
    )
    assert updated.status_code == 200
    assert updated.json()["checks"][0]["result"] == "Clear"
