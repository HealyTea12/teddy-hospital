from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image
from PIL.Image import Transpose


def test_upload(test_client: TestClient):
    # The new /upload endpoint requires form fields: first_name, last_name, animal_name, qr_content, animal_type, broken_bone
    data = {
        "first_name": "Test",
        "last_name": "User",
        "animal_name": "Eichhornchen",
        "qr_content": "1",
        "animal_type": "squirrel",
        "broken_bone": "false",
    }
    r1 = test_client.post(
        "/upload",
        files={"file": open("tests/img/eichhornchen.jpeg", "rb")},
        data=data,
    )
    assert r1.status_code == 200
    data["animal_name"] = "Teddy"
    data["animal_type"] = "bear"
    r2 = test_client.post(
        "/upload",
        files={"file": open("tests/img/teddy.jpg", "rb")},
        data=data,
    )
    assert r2.status_code == 200
    data["animal_name"] = "Own"
    data["animal_type"] = "other"
    r3 = test_client.post(
        "/upload",
        files={"file": open("tests/img/4k.jpg", "rb")},
        data=data,
    )
    assert r3.status_code == 200


def test_jobs(test_client: TestClient):
    response = test_client.get("/job")
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"
    img = Image.open(BytesIO(response.content))
    img_id = response.headers["img_id"]
    img = img.transpose(Transpose.FLIP_TOP_BOTTOM)
    # The /job POST endpoint expects image_id in header and result as file
    result_bytes = BytesIO()
    img.save(result_bytes, format="PNG")
    result_bytes.seek(0)
    r = test_client.post(
        "/job",
        data={"image_id": img_id},
        files={"result": ("test_result.png", result_bytes, "image/png")},
    )
    assert r.status_code == 200
    test_client.get("/job")
    test_client.get("/job")
    r = test_client.get("/job")
    assert r.status_code == 204
