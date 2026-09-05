from fastapi import FastAPI
from .routers.payments import router as payments_router
from .routers.auth import router as auth_router
from app.messaging.rabbitmq import create_connection,setup_rabbitmq

app = FastAPI()

channel = create_connection().channel()
setup_rabbitmq(channel)

app.include_router(payments_router)
app.include_router(auth_router)


