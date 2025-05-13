import pytest
from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture(scope="session")
def test_client():
    yield TestClient(app)
