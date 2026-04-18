from typing import Optional


def _create_session(
    client,
    *,
    end_user_ref: str,
    tenant_ref: Optional[str] = None,
    permissions: Optional[list[str]] = None,
) -> str:
    response = client.post(
        "/v1/sessions",
        json={
            "end_user_ref": end_user_ref,
            "tenant_ref": tenant_ref,
            "permissions": permissions or [],
        },
    )
    assert response.status_code == 201
    return response.json()["session_token"]


def _run_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_list_runs_requires_authenticated_session(client):
    response = client.get("/v1/runs")

    assert response.status_code == 401
    assert response.json() == {"detail": "Missing session token"}


def test_list_runs_is_scoped_to_current_end_user_without_tenant_wide_permission(client):
    alice_token = _create_session(
        client,
        end_user_ref="alice",
        tenant_ref="tenant_1",
    )
    bob_token = _create_session(
        client,
        end_user_ref="bob",
        tenant_ref="tenant_1",
    )

    alice_run = client.post(
        "/v1/runs",
        headers=_run_headers(alice_token),
        json={
            "action_id": "create_project",
            "inputs": {"name": "Alice project"},
        },
    )
    bob_run = client.post(
        "/v1/runs",
        headers=_run_headers(bob_token),
        json={
            "action_id": "create_project",
            "inputs": {"name": "Bob project"},
        },
    )

    assert alice_run.status_code == 200
    assert bob_run.status_code == 200

    response = client.get("/v1/runs", headers=_run_headers(alice_token))

    assert response.status_code == 200
    runs = response.json()
    assert len(runs) == 1
    assert runs[0]["end_user_ref"] == "alice"
    assert runs[0]["normalized_inputs"] == {"name": "Alice project"}


def test_list_runs_can_expand_to_tenant_scope_with_permission(client):
    admin_token = _create_session(
        client,
        end_user_ref="admin",
        tenant_ref="tenant_1",
        permissions=["runs:read_all_tenant"],
    )
    user_token = _create_session(
        client,
        end_user_ref="alice",
        tenant_ref="tenant_1",
    )
    other_tenant_token = _create_session(
        client,
        end_user_ref="eve",
        tenant_ref="tenant_2",
    )

    client.post(
        "/v1/runs",
        headers=_run_headers(admin_token),
        json={
            "action_id": "create_project",
            "inputs": {"name": "Admin project"},
        },
    )
    client.post(
        "/v1/runs",
        headers=_run_headers(user_token),
        json={
            "action_id": "create_project",
            "inputs": {"name": "Tenant project"},
        },
    )
    client.post(
        "/v1/runs",
        headers=_run_headers(other_tenant_token),
        json={
            "action_id": "create_project",
            "inputs": {"name": "Other tenant project"},
        },
    )

    response = client.get("/v1/runs", headers=_run_headers(admin_token))

    assert response.status_code == 200
    runs = response.json()
    assert len(runs) == 2
    assert {run["end_user_ref"] for run in runs} == {"admin", "alice"}


def test_run_rejects_invalid_inputs_against_action_contract(client):
    token = _create_session(
        client,
        end_user_ref="alice",
        tenant_ref="tenant_1",
    )

    response = client.post(
        "/v1/runs",
        headers=_run_headers(token),
        json={
            "action_id": "invite_team_member",
            "inputs": {
                "email": "not-an-email",
                "role": "owner",
                "unexpected": "value",
            },
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "failed"
    assert payload["message"] == "Provided inputs did not match the action contract."
    assert {field["key"] for field in payload["invalid_fields"]} == {
        "email",
        "role",
        "unexpected",
    }

    runs_response = client.get("/v1/runs", headers=_run_headers(token))
    runs = runs_response.json()
    assert runs[0]["status"] == "failed"
    assert {field["key"] for field in runs[0]["invalid_fields"]} == {
        "email",
        "role",
        "unexpected",
    }
