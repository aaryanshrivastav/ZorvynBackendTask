def _create_tx(client, token, owner_user_id, transaction_id, amount, tx_type="Credit", category="Payroll"):
    return client.post(
        "/transactions",
        json={
            "transaction_id": transaction_id,
            "occurred_at": "2025-01-10T10:00:00",
            "account_number": "ACC-100",
            "transaction_type": tx_type,
            "amount": amount,
            "currency": "USD",
            "counterparty": "Acme",
            "category": category,
            "payment_method": "Card",
            "owner_user_id": owner_user_id,
        },
        headers={"Authorization": f"Bearer {token}"},
    )


def test_viewer_scope_and_filters(client, admin_token, analyst_token, viewer_token):
    tx1 = _create_tx(client, analyst_token, 2, "T100", "100.00", "Credit", "Sales")
    assert tx1.status_code == 200
    tx2 = _create_tx(client, analyst_token, 2, "T101", "50.00", "Debit", "Ops")
    assert tx2.status_code == 200

    grant = client.post(
        "/admin/viewer-scopes",
        json={"viewer_user_id": 4, "scope_type": "ACCOUNT", "account_number": "ACC-100"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert grant.status_code == 200

    listed = client.get(
        "/transactions?category=Sales",
        headers={"Authorization": f"Bearer {viewer_token}"},
    )
    assert listed.status_code == 200
    assert listed.json()["total"] == 1


def test_dashboard_summary(client, analyst_token):
    assert _create_tx(client, analyst_token, 2, "T200", "200.00", "Credit").status_code == 200
    assert _create_tx(client, analyst_token, 2, "T201", "80.00", "Debit").status_code == 200

    summary = client.get("/dashboard/summary", headers={"Authorization": f"Bearer {analyst_token}"})
    assert summary.status_code == 200
    data = summary.json()
    assert float(data["total_income"]) == 200.0
    assert float(data["total_expenses"]) == 80.0
