from fastapi.testclient import TestClient
from app.main import app
from app.schemas import TransactionStatus
from app.model import TransactionStatusHistory
from sqlalchemy.orm import Session
from sqlalchemy import select
from concurrent.futures import ThreadPoolExecutor


client = TestClient(app)


def test_transaction_not_found(auth_headers):
    response = client.patch(
        "/api/v1/transactions/00000000-0000-0000-0000-000000000000/status",
        json={
            "status": "succeeded"
        },
        headers=auth_headers
    )

    assert response.status_code == 404


def test_transaction_status_update(auth_headers):
    response = client.post(
        "/api/v1/transactions/create",
        json={
            "transaction_type": "payment",
            "recipient_account_number": "000000000002",
            "amount": 100.55,
            "currency": "MYR"
        },
        headers={
            "Idempotency-Key": "test-transaction-status-update",
            **auth_headers
        }
    )

    assert response.status_code == 200

    transaction_id = response.json()["transaction_id"]

    response = client.patch(
        f"/api/v1/transactions/{transaction_id}/status",
        json={
            "status": "processing"
        },
        headers=auth_headers
    )

    assert response.status_code == 200
    assert (
        response.json()["status"]
        == TransactionStatus.PROCESSING.value
    )


def test_invalid_status_transition(
    db: Session,
    auth_headers
):
    # Create transaction
    response = client.post(
        "/api/v1/transactions/create",
        json={
            "transaction_type": "payment",
            "recipient_account_number": "000000000002",
            "amount": 100,
            "currency": "MYR"
        },
        headers={
            "Idempotency-Key": "test-invalid-transition",
            **auth_headers
        }
    )

    assert response.status_code == 200

    transaction_id = response.json()["transaction_id"]

    # Move PENDING → PROCESSING
    response = client.patch(
        f"/api/v1/transactions/{transaction_id}/status",
        json={
            "status": "processing"
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    # Test status history
    status_history = db.execute(
        select(TransactionStatusHistory).where(
            TransactionStatusHistory.transaction_id == transaction_id,
            TransactionStatusHistory.old_status
            == TransactionStatus.PENDING,
            TransactionStatusHistory.new_status
            == TransactionStatus.PROCESSING
        )
    ).scalar_one_or_none()

    assert status_history is not None

    # Try PROCESSING → CANCELLED
    response = client.patch(
        f"/api/v1/transactions/{transaction_id}/status",
        json={
            "status": "cancelled"
        },
        headers=auth_headers
    )

    assert response.status_code == 409


def test_idempotent_transaction_creation(auth_headers):

    payload = {
        "transaction_type": "payment",
        "recipient_account_number": "000000000002",
        "amount": 100,
        "currency": "MYR"
    }

    headers = {
        "Idempotency-Key": "same-transaction-key-123",
        **auth_headers
    }

    response1 = client.post(
        "/api/v1/transactions/create",
        json=payload,
        headers=headers
    )

    response2 = client.post(
        "/api/v1/transactions/create",
        json=payload,
        headers=headers
    )

    assert response1.status_code == response2.status_code

    assert (
        response1.json()["transaction_id"]
        == response2.json()["transaction_id"]
    )


def test_concurrent_update_transaction_status(
    auth_headers
):
    # Create transaction
    response = client.post(
        "/api/v1/transactions/create",
        json={
            "transaction_type": "payment",
            "recipient_account_number": "000000000002",
            "amount": 100,
            "currency": "MYR"
        },
        headers={
            "Idempotency-Key":
                "test-concurrent-update-transaction-status",
            **auth_headers
        }
    )

    assert response.status_code == 200

    transaction_id = response.json()["transaction_id"]

    # Move PENDING → PROCESSING
    response = client.patch(
        f"/api/v1/transactions/{transaction_id}/status",
        json={
            "status": "processing"
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    def update_to_succeeded():
        with TestClient(app) as client:
            return client.patch(
                f"/api/v1/transactions/{transaction_id}/status",
                json={
                    "status": "succeeded"
                },
                headers=auth_headers
            )

    def update_to_failed():
        with TestClient(app) as client:
            return client.patch(
                f"/api/v1/transactions/{transaction_id}/status",
                json={
                    "status": "failed"
                },
                headers=auth_headers
            )

    # Submit concurrent requests
    with ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(update_to_succeeded)
        future2 = executor.submit(update_to_failed)

        response1 = future1.result()
        response2 = future2.result()

    assert sorted(
        [
            response1.status_code,
            response2.status_code
        ]
    ) == [200, 409]