from datetime import date
from decimal import Decimal

from app.db.init_db import init_db


def _login(client, email: str, password: str) -> dict[str, str]:
    response = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


def test_salary_component_grouping_structure_versioning_and_preview(client, db):
    init_db(db)
    headers = _login(client, "admin@aihrms.com", "Admin@123456")

    component = client.post(
        "/api/v1/payroll/components",
        json={
            "name": "Basic",
            "code": "BASIC_TEST",
            "component_type": "Earning",
            "calculation_type": "Percentage",
            "amount": "40",
            "percentage_of": "ctc",
            "formula_expression": "ctc_monthly * 0.40",
            "payslip_group": "Earnings",
            "display_sequence": 10,
            "is_taxable": True,
        },
        headers=headers,
    )
    assert component.status_code == 201
    component_id = component.json()["id"]

    structure = client.post(
        "/api/v1/payroll/structures",
        json={
            "name": "Standard India CTC",
            "description": "Default monthly payroll structure",
            "version": "1.0",
            "effective_from": date(2026, 5, 1).isoformat(),
            "components": [{"component_id": component_id, "percentage": "40", "order_sequence": 10}],
        },
        headers=headers,
    )
    assert structure.status_code == 201
    structure_data = structure.json()
    assert structure_data["version"] == "1.0"
    assert structure_data["components"][0]["payslip_group"] == "Earnings"

    preview = client.post(
        f"/api/v1/payroll/structures/{structure_data['id']}/preview",
        json={"ctc": "1200000"},
        headers=headers,
    )
    assert preview.status_code == 200
    preview_data = preview.json()
    assert Decimal(str(preview_data["monthly_ctc"])) == Decimal("100000.00")
    assert Decimal(str(preview_data["lines"][0]["monthly_amount"])) == Decimal("40000.00")

    clone = client.post(
        f"/api/v1/payroll/structures/{structure_data['id']}/clone",
        params={"version": "1.1", "effective_from": "2026-06-01"},
        headers=headers,
    )
    assert clone.status_code == 201
    assert clone.json()["version"] == "1.1"
    assert clone.json()["parent_structure_id"] == structure_data["id"]
