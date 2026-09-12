# Payment Platform

A backend payment-processing simulation built with **FastAPI, PostgreSQL, SQLAlchemy, RabbitMQ, and Docker**.

The project focuses on reliable asynchronous payment processing and demonstrates backend engineering concepts such as **idempotency, state-machine validation, database transactions, row-level locking, message acknowledgements, retries with exponential backoff, dead-letter queues, publisher confirms, and the transactional outbox pattern**.

## Architecture

```text
                         ┌──────────────────┐
                         │      Client      │
                         └────────┬─────────┘
                                  │
                                  ▼
                         ┌──────────────────┐
                         │     FastAPI      │
                         │  REST API / JWT  │
                         └────────┬─────────┘
                                  │
                    ┌─────────────┴─────────────┐
                    ▼                           ▼
             ┌──────────────┐           ┌──────────────┐
             │  PostgreSQL  │           │   RabbitMQ   │
             │              │           │   Exchange   │
             │ Payments     │           └──────┬───────┘
             │ Users        │                  │
             │ History      │                  │
             │ Outbox       │                  ▼
             └──────┬───────┘           ┌──────────────┐
                    │                   │ Payment      │
                    │                   │ Worker       │
                    │                   └──────┬───────┘
                    │                          │
                    │                          │ Process
                    │                          ▼
                    │                   ┌──────────────┐
                    └───────────────────│ PostgreSQL   │
                                        └──────────────┘

                         Transactional Outbox
                                │
                                ▼
                         ┌──────────────┐
                         │ Outbox       │
                         │ Worker       │
                         └──────┬───────┘
                                │
                                ▼
                         ┌──────────────┐
                         │   RabbitMQ   │
                         │ Events / DLX  │
                         └──────┬───────┘
                                │
                         ┌──────┴──────┐
                         ▼             ▼
                  Event Consumers   Payment DLQ
```

## Key Features

### Authentication & Authorization

* JWT authentication
* Password hashing
* Role-based access control
* Customer, payment processor, and administrator roles
* Protected endpoints

### Payment Processing

* Create and retrieve payments
* Payment status management
* Supported currencies:

  * MYR
  * USD
  * SGD
* Payment state machine
* Payment status history
* UUID-based payment identifiers

### Idempotency

Payment creation supports an **idempotency key** to prevent duplicate payment creation when clients retry the same request.

If the same idempotency key is reused with a different request payload, the API rejects the request with a conflict response.

This models an important requirement in real payment systems where clients may retry requests because of network failures or timeouts.

### Asynchronous Processing

Payment processing is performed asynchronously using **RabbitMQ**.

The API does not wait for the simulated payment processing to finish.

```text
POST /payments
      │
      ▼
Create PENDING payment
      │
      ▼
Publish processing event
      │
      ▼
Return API response
      │
      ▼
RabbitMQ
      │
      ▼
Payment Worker
      │
      ▼
PROCESSING
      │
      ├───────────────┐
      ▼               ▼
  SUCCEEDED        FAILED
```

This separates the API request lifecycle from background payment processing.

## Payment State Machine

Payments are protected by an explicit state-transition model.

```text
                 ┌─────────────┐
                 │   PENDING   │
                 └──────┬──────┘
                        │
                        ▼
                 ┌─────────────┐
                 │ PROCESSING  │
                 └──────┬──────┘
                    ┌───┴───┐
                    ▼       ▼
             ┌──────────┐ ┌──────────┐
             │SUCCEEDED │ │  FAILED  │
             └──────────┘ └──────────┘

PENDING ───────────────► CANCELLED
```

Invalid transitions are rejected.

For example:

```text
SUCCEEDED → PROCESSING    ❌
FAILED → SUCCEEDED        ❌
CANCELLED → SUCCEEDED     ❌
```

This prevents workers or API requests from accidentally overwriting terminal payment states.

## Concurrency Control

Payment processing uses PostgreSQL row-level locking with:

```python
SELECT ... FOR UPDATE
```

The worker uses short database transactions to claim and finalize payments.

Database locks are not held while simulated processing or external operations are running.

This helps prevent concurrent workers from processing the same payment state transition incorrectly.

## RabbitMQ Retry System

Temporary payment-processing failures are retried asynchronously.

The retry system uses RabbitMQ TTL queues and dead-letter routing to implement exponential backoff.

```text
Temporary Failure
       │
       ▼
  Retry Attempt 1
       │
      2s
       │
       ▼
  Retry Attempt 2
       │
      4s
       │
       ▼
  Retry Attempt 3
       │
      8s
       │
       ▼
 Maximum Retries
       │
       ▼
     FAILED
```

Retry queues:

```text
payment.retry.2s
payment.retry.4s
payment.retry.8s
```

Each retry message contains a retry counter:

```json
{
    "payment_id": "...",
    "retry_count": 2
}
```

### Retry Classification

Errors are classified into two categories:

**Temporary errors**

Examples:

* transient processing failures
* temporary downstream failures
* recoverable infrastructure problems

These can be retried.

**Permanent errors**

These are immediately finalized as `FAILED` without further retries.

## Publisher Confirms

RabbitMQ publisher confirms are used when publishing important messages.

The publisher waits for RabbitMQ confirmation before acknowledging the original message where appropriate.

This reduces the risk of:

```text
Publish retry
      ↓
Publish fails
      ↓
ACK original message
      ↓
Retry message lost
```

Persistent RabbitMQ messages are also used for important events.

## Transactional Outbox

The project uses the **transactional outbox pattern** to reliably publish payment status events.

Instead of directly performing:

```text
Update database
      +
Publish RabbitMQ event
```

inside unrelated operations, the payment transaction records an outbox event in the same database transaction.

```text
┌─────────────────────────────┐
│ PostgreSQL Transaction      │
│                             │
│ Update Payment              │
│ Add Status History          │
│ Create Outbox Event         │
│                             │
│ COMMIT                      │
└──────────────┬──────────────┘
               │
               ▼
        Outbox Worker
               │
               ▼
           RabbitMQ
```

This prevents a successful database update from silently losing its corresponding event because RabbitMQ was temporarily unavailable.

The outbox worker periodically finds unpublished events and publishes them.

Events are marked as published only after successful message publication.

### Delivery Semantics

The outbox provides **at-least-once delivery**, rather than exactly-once delivery.

If RabbitMQ accepts an event but the database update marking the event as published fails, the event may be published again.

Consumers should therefore be designed to handle duplicate events safely.

Each outbox event has an `event_id` that can be used for deduplication.

## Dead-Letter Queue

Messages that cannot be successfully processed after the configured retry attempts are represented as failed payment events.

The architecture uses a RabbitMQ dead-letter exchange:

```text
payments.dlx
       │
       ▼
payment.dlq
```

The payment worker is responsible for payment state changes.

The outbox worker is responsible for publishing durable payment events.

This keeps database state management separate from message delivery.

## Database

PostgreSQL stores:

* Users
* Roles
* Payments
* Payment status history
* Idempotency records
* Outbox events

Database schema changes are managed using **Alembic migrations**.

Example:

```bash
alembic upgrade head
```

Create a migration:

```bash
alembic r
```
