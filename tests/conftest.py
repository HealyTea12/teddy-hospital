from os import PathLike

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

    def upload_file(self, user_ref: int | str, type: str, file_path: PathLike | int):
        self.storage[user_ref][type] = open(file_path, "rb").read()


@pytest.fixture(scope="session")
def test_client():
    yield TestClient(app)


@pytest.fixture()
def mock_storage():
    return MockStorage()
