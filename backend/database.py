from pymongo import MongoClient
import gridfs
from config import MONGO_URI, DB_NAME


client = MongoClient(MONGO_URI)
db = client[DB_NAME]
fs = gridfs.GridFS(db, collection="Plots")

def save_audio_to_db(filename, audio_data):
    """Save audio file to MongoDB GridFS."""
    with fs.new_file(filename=filename, content_type="audio/wav") as f:
        f.write(audio_data)
    return f._id

def save_plot_to_db(filename, plot_data):
    """Save plot image to MongoDB GridFS."""
    with fs.new_file(filename=filename, content_type="image/png") as f:
        f.write(plot_data)
    return f._id

def fetch_file(file_id):
    """Retrieve file from MongoDB GridFS."""
    return fs.get(file_id)


# to mongo -------------------
audio_fs = gridfs.GridFS(db, collection="Audio")
def save_audio_to_audio_collection(filename, audio_data):
    """Save audio file to MongoDB GridFS."""
    with audio_fs.new_file(filename=filename, content_type="audio/wav") as f:
        f.write(audio_data)
    return f._id


from flask import jsonify
import base64
from io import BytesIO
from database import fetch_file  # Ensure fetch_file retrieves by filename

def fetch_plots(obj_id):
    """
    Fetch an image from MongoDB GridFS by filename and return it as a Base64 string.
    """
    try:
        image_file = fetch_file(filename)  # Fetch file from GridFS
        print("---"*50)
        print(image_file)
        print("---"*50)
        return base64.b64encode(image_file.read()).decode("utf-8")  # Return only Base64

    except Exception as e:
        print(f"Error fetching plot {filename}: {e}")
        return None  # Return None instead of JSON
    




from flask import Flask, Response
from pymongo import MongoClient
from bson import ObjectId
import gridfs

def fetch_plots_new(file_id):
    try:
        # Convert string ID to ObjectId
        obj_id = ObjectId(file_id)
        
        # Retrieve file from GridFS
        file_data = fs.get(obj_id)

        # Encode file in Base64
        image_base64 = base64.b64encode(file_data.read()).decode('utf-8')

        # Return JSON response
        return jsonify({"image": image_base64})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 404