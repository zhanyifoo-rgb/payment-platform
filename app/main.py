from fastapi import FastAPI
from .routers.payments import router as payments_router
from .routers.auth import router as auth_router

app = FastAPI()

app.include_router(payments_router)
app.include_router(auth_router)


