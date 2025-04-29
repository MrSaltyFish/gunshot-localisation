import pytest
import os
from io import BytesIO
from backend.app import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    client = app.test_client()
    yield client

def test_index_route(client):
    """Test if the index route is accessible"""
    response = client.get("/")
    assert response.status_code == 200

def test_upload_no_file(client):
    """Test /upload without sending a file"""
    response = client.post("/upload")
    assert response.status_code == 404
    assert b"No file uploaded" in response.data

def test_upload_valid_file(client):
    """Test file upload functionality"""
    test_audio = BytesIO(b"Fake WAV file content")
    data = {"file": (test_audio, "test.wav"), "mic_coords": "10.0,20.0"}
    response = client.post("/upload", data=data, content_type="multipart/form-data")
    assert response.status_code == 200
    assert b"doa_rad" in response.data

def test_fetch_plot_invalid(client):
    """Test fetching a non-existing plot"""
    response = client.get("/fetch_plot/nonexistent.png")
    assert response.status_code == 404
