# Payment Platform

A backend payment-processing simulation built with **FastAPI, PostgreSQL, SQLAlchemy, Alembic, RabbitMQ, and Docker**.

## Features

* JWT authentication & role-based authorization
* Payment creation and status management
* Idempotency keys
* Payment status history
* Asynchronous payment processing with RabbitMQ
* PostgreSQL database
* Alembic database migrations
* Automated tests

## Tech Stack

* Python
* FastAPI
* PostgreSQL
* SQLAlchemy
* Alembic
* RabbitMQ
* Docker
* Pytest

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/zhanyifoo-rgb/payment-platform.git
cd payment-platform
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start PostgreSQL and RabbitMQ

Start the required Docker services:

```bash
docker compose up -d
```

Check that they are running:

```bash
docker ps
```

RabbitMQ Management UI:

```text
http://localhost:15672
```

### 5. Configure environment variables

Create a `.env` file in the project root:

```env
DATABASE_URL=postgresql+psycopg://username:password@localhost:5432/paymentdb
SECRET_KEY=your-secret-key
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672
```

Use the database credentials configured in your Docker Compose file.

### 6. Run database migrations

```bash
alembic upgrade head
```

### 7. Start the FastAPI application

Open **Terminal 1**:

```bash
uvicorn app.main:app --reload
```

API:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

### 8. Start the payment worker

Open **Terminal 2**:

```bash
python -m app.workers.payments_worker
```

You should see:

```text
Worker waiting for messages...
```

Keep the worker running while using the API.

## Running the Application

The payment flow is:

```text
Client
  ↓
FastAPI
  ↓
PostgreSQL
  ↓
RabbitMQ
  ↓
Payment Worker
  ↓
PostgreSQL
```

When a payment is created, it starts as `pending`. The worker processes it asynchronously and updates the payment to `processing`, followed by `succeeded` or `failed`.

## Run Tests

```bash
pytest
```

## Useful Commands

Stop Docker services:

```bash
docker compose down
```

View container logs:

```bash
docker compose logs
```

Run migrations:

```bash
alembic upgrade head
```

Create a migration:

```bash
alembic revision --autogenerate -m "description"
```
