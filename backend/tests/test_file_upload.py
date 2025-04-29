import os
from app import UPLOAD_FOLDER

def test_upload_folder_exists():
    """Ensure the upload directory is created"""
    assert os.path.exists(UPLOAD_FOLDER)
