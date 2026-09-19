from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.payments import router as payments_router
from .routers.auth import router as auth_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",
        "http://127.0.0.1:5500",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(payments_router)
app.include_router(auth_router)