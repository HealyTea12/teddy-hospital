import mimetypes
import os
from typing import Union

import qrcode
import reportlab.pdfgen
import reportlab.pdfgen.canvas
import toml
import uvicorn
from anyio import Path
from fastapi import FastAPI, Query, Response
from fastapi.responses import FileResponse
from pydantic import BaseModel
from seafileapi import SeafileAPI

from routes import api

app = FastAPI()
app.include_router(api.router)
