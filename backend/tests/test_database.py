import pytest
from database import save_audio_to_db, fetch_file

@pytest.fixture
def fake_audio():
    return b"Fake WAV content"

def test_save_audio_to_db(fake_audio):
    """Test saving an audio file to MongoDB"""
    file_id = save_audio_to_db("test.wav", fake_audio)
    assert file_id is not None

def test_fetch_non_existent_file():
    """Test fetching a non-existent file"""
    file = fetch_file("nonexistent.wav")
    assert file is None
