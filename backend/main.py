from typing import Union

from anyio import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import api

app = FastAPI()
app.include_router(api.router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_methods=["GET"],
    allow_headers=["*"],
)
