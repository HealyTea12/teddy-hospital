from enum import Enum
from io import BytesIO
import io
from tempfile import SpooledTemporaryFile
from types import SimpleNamespace
from typing import List
from unittest.mock import MagicMock

import requests
from fastapi.testclient import TestClient
from PIL import Image
from PIL.Image import Transpose
from pydantic import BaseModel

from backend.routes import api

# test upload route
# expected: status code 200
def test_upload(test_client: TestClient):

    form_data = {
        "first_name": "Max",
        "last_name": "Mustermann",
        "animal_name": "Teddy",
        "qr_content": "user001",
    }

    r1 = test_client.post(
        "/upload",
        files={"file": open("tests/img/eichhornchen.jpeg", "rb")},
        data=form_data,
    )
    assert r1.status_code == 200
    test_client.post(
        "/upload",
        files={"file": open("tests/img/teddy.jpg", "rb")},
        data=form_data,
    )
    assert r1.status_code == 200
    test_client.post(
        "/upload",
        files={"file": open("tests/img/own.jpg", "rb")},
        data=form_data,
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

# test get_job without any jobs in queue, use MagicMock to simulate an empty queue
# expected: code 200 with text "No jobs in queue"
def test_get_job_no_jobs(test_client: TestClient, monkeypatch):
    # Mock JobQueue to return None
    mock_queue = MagicMock()
    mock_queue.get_job.return_value = None
    monkeypatch.setattr(api, "job_queue", mock_queue)

    response = test_client.get("/job")
    assert response.status_code == 200
    assert "No Jobs in queue" in response.text

# test get_job with job in queue
# expected: code 200 with image data same as the mock job defined in the test
def test_get_job_job_in_queue(test_client: TestClient, monkeypatch):
    # Create a mock job
    mock_file = SpooledTemporaryFile()
    mock_file.write(b"fake image data")
    mock_file.seek(0)

    mock_job = SimpleNamespace(
        file=mock_file,
        id=123,
        first_name="Max",
        last_name="Mustermann",
        animal_name="Teddy",
    )

    mock_queue = MagicMock()
    mock_queue.get_job.return_value = mock_job
    monkeypatch.setattr(api, "job_queue", mock_queue)

    response = test_client.get("/job")
    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.headers["img_id"] == "123"
    assert response.headers["first_name"] == "Max"
    assert response.headers["last_name"] == "Mustermann"
    assert response.headers["animal_name"] == "Teddy"
    assert response.content == b"fake image data"


# test uploading job
# expected: a response with code 200
def test_conclude_job(test_client: TestClient, monkeypatch):
    mock_queue = MagicMock()
    monkeypatch.setattr(api, "job_queue", mock_queue)
    mock_queue.submit_job.return_value = None

    dummy_result = io.BytesIO(b"x-ray image")
    files = {"result": ("result.png", dummy_result, "image/png")}
    headers = {"image_id": "1"}
    response = test_client.post("/job", files=files, headers=headers)
    assert response.status_code in (200)


# test confirming a picture
# expected: code 200
def test_confirm_job(client, monkeypatch):
    mock_queue = MagicMock()
    monkeypatch.setattr(api, "job_queue", mock_queue)
    mock_queue.confirm_job.return_value = None

    params = {"image_id": 1, "choice": 0, "confirm": True}
    response = client.get("/confirm", params=params)
    assert response.status_code == 200

# TODO results test are missing
