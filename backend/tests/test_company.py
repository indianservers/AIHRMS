def test_company_static_routes_resolve(client, superuser_headers):
    responses = [
        client.get("/api/v1/company/branches/", headers=superuser_headers),
        client.get("/api/v1/company/departments/", headers=superuser_headers),
        client.get("/api/v1/company/designations/", headers=superuser_headers),
    ]

    assert [response.status_code for response in responses] == [200, 200, 200]


def test_create_company_rejects_duplicate_name(client, superuser_headers):
    payload = {"name": "Acme India", "country": "India"}

    first = client.post("/api/v1/company/", json=payload, headers=superuser_headers)
    second = client.post("/api/v1/company/", json={"name": "acme india"}, headers=superuser_headers)

    assert first.status_code == 201
    assert second.status_code == 409


def test_create_branch_requires_active_company(client, superuser_headers):
    response = client.post(
        "/api/v1/company/branches/",
        json={"name": "HQ", "company_id": 999999},
        headers=superuser_headers,
    )

    assert response.status_code == 404


def test_create_branch_rejects_duplicate_name_in_company(client, superuser_headers):
    company = client.post(
        "/api/v1/company/",
        json={"name": "Branch Parent"},
        headers=superuser_headers,
    ).json()
    payload = {"name": "Mumbai", "code": "MUM", "company_id": company["id"]}

    first = client.post("/api/v1/company/branches/", json=payload, headers=superuser_headers)
    second = client.post(
        "/api/v1/company/branches/",
        json={"name": "mumbai", "code": "MUM2", "company_id": company["id"]},
        headers=superuser_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_create_department_rejects_duplicate_code_in_branch(client, superuser_headers):
    company = client.post(
        "/api/v1/company/",
        json={"name": "Department Parent"},
        headers=superuser_headers,
    ).json()
    branch = client.post(
        "/api/v1/company/branches/",
        json={"name": "HQ", "company_id": company["id"]},
        headers=superuser_headers,
    ).json()

    first = client.post(
        "/api/v1/company/departments/",
        json={"name": "Engineering", "code": "ENG", "branch_id": branch["id"]},
        headers=superuser_headers,
    )
    second = client.post(
        "/api/v1/company/departments/",
        json={"name": "Product Engineering", "code": "eng", "branch_id": branch["id"]},
        headers=superuser_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 409


def test_create_designation_rejects_duplicate_name_in_department(client, superuser_headers):
    company = client.post(
        "/api/v1/company/",
        json={"name": "Designation Parent"},
        headers=superuser_headers,
    ).json()
    branch = client.post(
        "/api/v1/company/branches/",
        json={"name": "HQ", "company_id": company["id"]},
        headers=superuser_headers,
    ).json()
    department = client.post(
        "/api/v1/company/departments/",
        json={"name": "Engineering", "branch_id": branch["id"]},
        headers=superuser_headers,
    ).json()

    first = client.post(
        "/api/v1/company/designations/",
        json={"name": "Software Engineer", "department_id": department["id"]},
        headers=superuser_headers,
    )
    second = client.post(
        "/api/v1/company/designations/",
        json={"name": "software engineer", "department_id": department["id"]},
        headers=superuser_headers,
    )

    assert first.status_code == 201
    assert second.status_code == 409
