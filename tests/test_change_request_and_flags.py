def _create_tx(client, token, txid):
    return client.post(
        "/transactions",
        json={
            "transaction_id": txid,
            "occurred_at": "2025-01-11T10:00:00",
            "account_number": "ACC-999",
            "transaction_type": "Credit",
            "amount": "111.00",
            "currency": "USD",
            "counterparty": "Ops",
            "category": "Ops",
            "payment_method": "Cash",
            "owner_user_id": 2,
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def test_update_and_delete_request_flow(client, analyst_token, approver_token):
    tx = _create_tx(client, analyst_token, "T300")
    tx_id = tx.json()["id"]

    update_req = client.post(
        "/change-requests/update",
        json={"transaction_id": tx_id, "reason": "Fix category", "proposed_changes": {"category": "Reconciled"}},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert update_req.status_code == 201

    review = client.post(
        f"/change-requests/{update_req.json()['id']}/review",
        json={"decision": "APPROVE"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert review.status_code == 200

    delete_req = client.post(
        "/change-requests/delete",
        json={"transaction_id": tx_id, "reason": "Duplicate"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert delete_req.status_code == 201

    duplicate = client.post(
        "/change-requests/delete",
        json={"transaction_id": tx_id, "reason": "Duplicate2"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert duplicate.status_code == 409

    review_delete = client.post(
        f"/change-requests/{delete_req.json()['id']}/review",
        json={"decision": "APPROVE"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert review_delete.status_code == 200

    list_active = client.get("/transactions", headers={"Authorization": f"Bearer {analyst_token}"})
    assert list_active.status_code == 200
    assert list_active.json()["total"] == 0


def test_flags_and_audit_logs(client, analyst_token, approver_token, admin_token):
    tx = _create_tx(client, analyst_token, "T301")
    tx_id = tx.json()["id"]

    create_flag = client.post(
        "/flags",
        json={"transaction_id": tx_id, "reason": "Suspicious"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert create_flag.status_code == 201

    review = client.patch(
        f"/flags/{create_flag.json()['id']}",
        json={"status": "RESOLVED"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert review.status_code == 200

    logs = client.get("/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert logs.status_code == 200
    assert logs.json()["total"] > 0


def test_change_request_rejects_non_whitelisted_fields(client, analyst_token):
    tx = _create_tx(client, analyst_token, "T302")
    tx_id = tx.json()["id"]

    invalid_update = client.post(
        "/change-requests/update",
        json={
            "transaction_id": tx_id,
            "reason": "Try to mutate protected field",
            "proposed_changes": {"amount": "999.99"},
        },
        headers={"Authorization": f"Bearer {analyst_token}"},
    )

    assert invalid_update.status_code == 409


def test_change_request_visibility_is_restricted(client, analyst_token, approver_token, viewer_token, admin_token):
    tx = _create_tx(client, analyst_token, "T303")
    tx_id = tx.json()["id"]

    created = client.post(
        "/change-requests/update",
        json={"transaction_id": tx_id, "reason": "Fix category", "proposed_changes": {"category": "Reviewed"}},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert created.status_code == 201
    request_id = created.json()["id"]

    viewer_get = client.get(f"/change-requests/{request_id}", headers={"Authorization": f"Bearer {viewer_token}"})
    assert viewer_get.status_code == 403

    approver_get = client.get(f"/change-requests/{request_id}", headers={"Authorization": f"Bearer {approver_token}"})
    assert approver_get.status_code == 200

    admin_get = client.get(f"/change-requests/{request_id}", headers={"Authorization": f"Bearer {admin_token}"})
    assert admin_get.status_code == 200


def test_invalid_flag_status_is_rejected(client, analyst_token, approver_token):
    tx = _create_tx(client, analyst_token, "T304")
    tx_id = tx.json()["id"]

    create_flag = client.post(
        "/flags",
        json={"transaction_id": tx_id, "reason": "Suspicious"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert create_flag.status_code == 201

    invalid_review = client.patch(
        f"/flags/{create_flag.json()['id']}",
        json={"status": "INVALID"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert invalid_review.status_code == 422


def test_resolved_flag_cannot_be_reviewed_twice(client, analyst_token, approver_token):
    tx = _create_tx(client, analyst_token, "T305")
    tx_id = tx.json()["id"]

    create_flag = client.post(
        "/flags",
        json={"transaction_id": tx_id, "reason": "Suspicious"},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert create_flag.status_code == 201

    first_review = client.patch(
        f"/flags/{create_flag.json()['id']}",
        json={"status": "RESOLVED"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert first_review.status_code == 200

    second_review = client.patch(
        f"/flags/{create_flag.json()['id']}",
        json={"status": "OPEN"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert second_review.status_code == 409


def test_change_request_cannot_be_reviewed_twice(client, analyst_token, approver_token):
    tx = _create_tx(client, analyst_token, "T306")
    tx_id = tx.json()["id"]

    update_req = client.post(
        "/change-requests/update",
        json={"transaction_id": tx_id, "reason": "Fix category", "proposed_changes": {"category": "Reconciled"}},
        headers={"Authorization": f"Bearer {analyst_token}"},
    )
    assert update_req.status_code == 201

    first_review = client.post(
        f"/change-requests/{update_req.json()['id']}/review",
        json={"decision": "APPROVE"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert first_review.status_code == 200

    second_review = client.post(
        f"/change-requests/{update_req.json()['id']}/review",
        json={"decision": "REJECT"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert second_review.status_code == 409
