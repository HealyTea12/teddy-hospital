import requests


def test_upload():
    url = "http://localhost:8000/upload/"
    requests.post(
        url,
        files={"file": open("tests/img/eichhornchen.jpeg", "rb")},
        params={"uid": 1},
    )
    requests.post(
        url,
        files={"file": open("tests/img/teddy.jpg", "rb")},
        params={"uid": 1},
    )
    requests.post(
        url,
        files={"file": open("tests/img/own.jpg", "rb")},
        params={"uid": 1},
    )


def test_get_jobs():
    url = "http://localhost:8000/job"
    response = requests.get(url)
    assert response.status_code == 200
    with open("tests/test_results/test.png", "wb") as f:
        f.write(response.content)


if __name__ == "__main__":
    # test_upload()
    # test_get_jobs()
    pass
