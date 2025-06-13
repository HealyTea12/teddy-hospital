from os import PathLike
from typing import IO

import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.storage import Storage


class MockStorage(Storage):
    def __init__(self):
        self.storage = {}
        self.id = 0

    def create_storage_for_user(self) -> str:
        self.storage[self.id] = {"normal": {}, "xray": {}}
        self.id += 1

    def upload_file(self, user_ref: int | str, type: str, file_path: PathLike | IO):
        if isinstance(file_path, PathLike):
            file_data = open(file_path, "rb")
        else:
            file_data = file_path
            file_data.seek(0)
        self.storage[user_ref][type] = file_data.read()


@pytest.fixture(scope="session")
def test_client():
    tc = TestClient(app)
    response = tc.post("/token", data={"password": "secret"})
    response.raise_for_status()
    token = response.json().get("access_token")
    tc.headers.update({"Authorization": f"Bearer {token}"})
    return tc


@pytest.fixture()
def mock_storage():
    return MockStorage()
