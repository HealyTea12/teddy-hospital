import requests
from fastapi.testclient import TestClient


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
    with open("tests/test_results/test.png", "wb") as f:
        f.write(response.content)
