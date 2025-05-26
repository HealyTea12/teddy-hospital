from io import BytesIO
import os
import pytest
from fastapi.testclient import TestClient

from backend.main import app

# use --durations={n} as option in pytest to measure slowest n tests


# test generating 0 QR codes
# expected: error message
def test_mkqr_0(test_client):
    response = test_client.get("/qr?n=0")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/plain; charset=utf-8"
    assert response.text == "No QR codes generated"


# test generating 3 QR codes
# expected: 3 QR codes in PDF format
# TODO check if there are actually 3 QR codes
def test_mkqr_3(test_client):
    response = test_client.get("/qr?n=3")
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"
    assert response.headers["content-disposition"] == 'attachment; filename="qr.pdf"'

# test generating 1000 QR codes
# expected: 1000 QR codes in PDF format
# TODO check if there are actually 1000 QR codes
#def test_mkqr_1000(test_client):
 #   response = test_client.get("/qr?n=1000")
  #  assert response.status_code == 200
   # assert response.headers["content-type"] == "application/pdf"
    #assert response.headers["content-disposition"] == 'attachment; filename="qr.pdf"'
