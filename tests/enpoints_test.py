from enum import Enum
from io import BytesIO
from typing import List

import requests
from fastapi.testclient import TestClient
from PIL import Image
from PIL.Image import Transpose
from pydantic import BaseModel


def test_upload(test_client: TestClient):
    r1 = test_client.post(
        "/upload",
        files={"file": open("tests/img/eichhornchen.jpeg", "rb")},
        params={"uid": 1},
    )
    assert r1.status_code == 200
    test_client.post(
        "/upload",
        files={"file": open("tests/img/teddy.jpg", "rb")},
        params={"uid": 1},
    )
    assert r1.status_code == 200
    test_client.post(
        "/upload",
        files={"file": open("tests/img/own.jpg", "rb")},
        params={"uid": 1},
    )
    assert r1.status_code == 200


def test_get_jobs(test_client: TestClient):

    response = test_client.get("/job")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    img = Image.open(BytesIO(response.content))
    img_id = response.headers["img_id"]
    img = img.transpose(Transpose.FLIP_TOP_BOTTOM)
    test_client.post(
        "/job",
        data={"image_id": img_id},
        files={"result": ("test_result.png", img.tobytes(), "image/png")},
    )
