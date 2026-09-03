from fastapi.testclient import TestClient
from app.main import app
from app.schemas import PaymentStatus
from app.model import PaymentStatusHistory
from sqlalchemy.orm import Session
from sqlalchemy import select
from concurrent.futures import ThreadPoolExecutor

client = TestClient(app)

def test_payment_not_found(auth_headers):
    response = client.patch(
        "/payments/00000000-0000-0000-0000-000000000000/status",
        json = {
            "status": "succeeded"
        },
        headers=auth_headers
    )

    assert response.status_code == 404

def test_payment_status_update(auth_headers):
    response = client.post(
        "/payments",
        json = {
            "user_id": 13533,
            "amount": 100.55,
            "currency": "MYR"
        },
        headers={
            "Idempotency-key" : "test-13533"
        }.update(auth_headers)
    )

    payment_id = response.json()["payment_id"]
    
    response = client.patch(
        f"/payments/{payment_id}/status",
        json = {
            "status": "processing"
        },
        headers=auth_headers

    )
    
    assert response.status_code == 200
    assert response.json()["status"] == PaymentStatus.PROCESSING.value

def test_invalid_status_transition(db: Session,auth_headers):
    # Create payment
    response = client.post(
        "/payments",
        json={
            "user_id": 13533,
            "amount": 100,
            "currency": "MYR"
        },
        headers={
            "Idempotency-Key": "test-invalid-transition"
        }.update(auth_headers)
    )
    
    payment_id = response.json()["payment_id"]

    # Move PENDING → PROCESSING
    response = client.patch(
        f"/payments/{payment_id}/status",
        json={
            "status": "processing"
        },
        headers=auth_headers
    )

    assert response.status_code == 200

    # test status history
    status_history = db.execute(select(PaymentStatusHistory).where(PaymentStatusHistory.payment_id == payment_id,
                                                                        PaymentStatusHistory.old_status == PaymentStatus.PENDING,
                                                                        PaymentStatusHistory.new_status == PaymentStatus.PROCESSING)).scalar_one_or_none()

    assert status_history is not None
   
    # Try PROCESSING → CANCELLED
    response = client.patch(
        f"/payments/{payment_id}/status",
        json={
            "status": "cancelled"
        },
        headers=auth_headers
    )

    assert response.status_code == 409


def test_idempotent_payment_creation(auth_headers):

    payload = {
            "user_id": 13533,
            "amount": 100,
            "currency": "MYR"
        }
    
    headers={
            "Idempotency-Key": "same-key-123"
        }.update(auth_headers)

    response1 = client.post(
        "/payments",
        json=payload,
        headers=headers
    )

    response2 = client.post(
        "/payments",
        json=payload,
        headers=headers
    )

    assert response1.status_code == response2.status_code

    assert (
        response1.json()["payment_id"]
        == response2.json()["payment_id"]
    )

    def test_concurrent_update_payment_status(auth_headers):
        # Create payment
            response = client.post(
                "/payments",
                json={
                    "user_id": 135343,
                    "amount": 100,
                    "currency": "MYR"
                },
                headers={
                    "Idempotency-Key": "test_concurrent_update_payment_status"
                }.update(auth_headers)
            )
            
            payment_id = response.json()["payment_id"]
        
            # Move PENDING → PROCESSING
            response = client.patch(
                f"/payments/{payment_id}/status",
                json={
                    "status": "processing"
                },
                headers=auth_headers
            )

            def update_to_succeeded():
                with TestClient(app) as client:
                    return client.patch(
                            f"/payments/{payment_id}/status",
                            json={
                                "status": "succeeded"
                            },
                            headers=auth_headers
                        )

            def update_to_failed():
                with TestClient(app) as client:
                    return client.patch(
                            f"/payments/{payment_id}/status",
                            json={
                                "status": "failed"
                            },
                            headers=auth_headers
                        )

            # submit concurrent request 
            with ThreadPoolExecutor(max_workers=2) as executor:
                 future1 = executor.submit(update_to_succeeded)
                 future2 = executor.submit(update_to_failed)

                 response1 = future1.result()
                 response2 = future2.result()

            assert sorted([response1.status_code,response2.status_code]) == [200,409]

