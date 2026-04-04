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
    assert update_req.status_code == 200

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
    assert delete_req.status_code == 200

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
    assert create_flag.status_code == 200

    review = client.patch(
        f"/flags/{create_flag.json()['id']}",
        json={"status": "RESOLVED"},
        headers={"Authorization": f"Bearer {approver_token}"},
    )
    assert review.status_code == 200

    logs = client.get("/audit-logs", headers={"Authorization": f"Bearer {admin_token}"})
    assert logs.status_code == 200
    assert logs.json()["total"] > 0
