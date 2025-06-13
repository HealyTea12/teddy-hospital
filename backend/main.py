from typing import Union

from anyio import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routes import api

app = FastAPI()
app.include_router(api.router)
# allow all cors because it probably doesn't matter in our case
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)
