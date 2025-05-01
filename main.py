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

import api
from storage import SeafileStorage, Storage

app = FastAPI()
app.include_router(api.router)


if __name__ == "__main__":

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
