from app.apps.crm.models import CRMLead


def test_crm_leads_crud_is_scoped_to_current_organization(client, db, superuser_headers):
    db.add(
        CRMLead(
            organization_id=2,
            first_name="Other",
            full_name="Other Org Lead",
            email="other@example.com",
            status="New",
        )
    )
    db.commit()

    created = client.post(
        "/api/v1/crm/leads",
        headers=superuser_headers,
        json={
            "firstName": "Rahul",
            "lastName": "Mehta",
            "fullName": "Rahul Mehta",
            "email": "rahul@example.com",
            "companyName": "Apex Digital",
            "status": "Qualified",
        },
    )
    assert created.status_code == 201
    lead_id = created.json()["id"]
    assert created.json()["organizationId"] == 1
    assert created.json()["createdBy"] is not None

    listed = client.get("/api/v1/crm/leads", headers=superuser_headers, params={"search": "Rahul"})
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["id"] == lead_id
    assert all(item["organizationId"] == 1 for item in listed.json()["items"])

    patched = client.patch(
        f"/api/v1/crm/leads/{lead_id}",
        headers=superuser_headers,
        json={"status": "Converted"},
    )
    assert patched.status_code == 200
    assert patched.json()["status"] == "Converted"
    assert patched.json()["updatedBy"] is not None

    deleted = client.delete(f"/api/v1/crm/leads/{lead_id}", headers=superuser_headers)
    assert deleted.status_code == 200

    after_delete = client.get("/api/v1/crm/leads", headers=superuser_headers, params={"include_deleted": False})
    assert all(item["id"] != lead_id for item in after_delete.json()["items"])


def test_crm_validates_unknown_entity_and_required_fields(client, superuser_headers):
    missing_required = client.post("/api/v1/crm/products", headers=superuser_headers, json={"sku": "NO-NAME"})
    assert missing_required.status_code == 422

    unknown = client.get("/api/v1/crm/unknown-resource", headers=superuser_headers)
    assert unknown.status_code == 404


def test_crm_custom_field_values_are_persisted_and_org_scoped(client, superuser_headers):
    field = client.post(
        "/api/v1/crm/custom-fields",
        headers=superuser_headers,
        json={"entity": "leads", "fieldKey": "preferred_plan", "label": "Preferred Plan", "fieldType": "text"},
    )
    assert field.status_code == 201

    value = client.post(
        "/api/v1/crm/custom-field-values",
        headers=superuser_headers,
        json={
            "customFieldId": field.json()["id"],
            "entity": "leads",
            "recordId": 1001,
            "valueText": "Enterprise",
        },
    )
    assert value.status_code == 201
    assert value.json()["organizationId"] == 1
    assert value.json()["createdBy"] is not None

    listed = client.get(
        "/api/v1/crm/custom-field-values",
        headers=superuser_headers,
        params={"entity": "leads", "record_id": 1001},
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1
    assert listed.json()["items"][0]["value_text"] == "Enterprise"
