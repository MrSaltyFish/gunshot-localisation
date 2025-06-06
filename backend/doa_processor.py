import os
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for Matplotlib
import librosa
import matplotlib.pyplot as plt
import os
import numpy as np
from geopy.distance import geodesic


PLOT_FOLDER = "static/plots"
os.makedirs(PLOT_FOLDER, exist_ok=True)
# Constants
SPEED_OF_SOUND = 343  # Speed of sound in air (m/s)
MIC_DISTANCE = 0.1     # Distance between adjacent microphones (adjust as needed)
RADIUS = 1             # Assume unit radius for Cartesian conversion

# Define Bias Ranges (adjust based on real setup)
BIAS_1_3 = (-0.00002, 0.00002)  # Bias for Mic 3
BIAS_1_4 = (-0.00003, 0.00003)  # Bias for Mic 4

def compute_tdoa(audio, sr):
    """Compute TDOA for given audio channels."""
    if audio.shape[0] < 2:
        return None
    
    channel_1 = audio[0, :]
    tdoa_values = []
    for i in range(1, audio.shape[0]):
        correlation = np.correlate(channel_1, audio[i, :], mode="full")
        delay = np.argmax(correlation) - (len(channel_1) - 1)
        tdoa_values.append(delay / sr)
    
    return tdoa_values if len(tdoa_values) == 3 else [0, 0, 0]

def extract_features(file_path):
    """Extract TDOA values from WAV file and apply bias."""
    try:
        y, sr = librosa.load(file_path, sr=None, mono=False)
        if len(y.shape) == 1:
            y = np.vstack([y, y, y, y])

        tdoa_1_2, _, _ = compute_tdoa(y, sr)
        tdoa_1_3 = tdoa_1_2 + np.random.uniform(*BIAS_1_3)
        tdoa_1_4 = tdoa_1_2 + np.random.uniform(*BIAS_1_4)

        return {
            "Filename": os.path.basename(file_path),
            "TDOA_1_2": tdoa_1_2,
            "TDOA_1_3": tdoa_1_3,
            "TDOA_1_4": tdoa_1_4
        }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

def calculate_doa(tdoa_1_2, tdoa_1_3, tdoa_1_4):
    """Calculate DOA from TDOA values."""
    doa_1_2 = np.degrees(np.arcsin((SPEED_OF_SOUND * tdoa_1_2) / MIC_DISTANCE))
    doa_1_3 = np.degrees(np.arcsin((SPEED_OF_SOUND * tdoa_1_3) / (2 * MIC_DISTANCE)))
    doa_1_4 = np.degrees(np.arcsin((SPEED_OF_SOUND * tdoa_1_4) / (1.2 * MIC_DISTANCE)))
    return np.mean([doa_1_2, doa_1_3, doa_1_4]) 

def plot_polar(doa):
    """Plot polar coordinates."""
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    doa_rad = np.radians(doa)
    ax.scatter(doa_rad, 1, color='b', label="Gunshot Direction")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rticks([])
    ax.set_title("Polar Plot of DOA", va="bottom")
    ax.legend()
    plt.savefig(os.path.join(PLOT_FOLDER, "polar.png"))  # Ensure correct path
    plt.close()

def plot_cartesian(x, y):
    """Plot Cartesian coordinates."""
    plt.figure(figsize=(8, 8))
    plt.scatter(x, y, color='b', marker='o', label="Gunshot Location", s=100)
    plt.scatter(0, 0, color='r', marker='x', s=200, label="Microphone (Reference)")
    plt.axhline(0, color='gray', linestyle='--', linewidth=1)
    plt.axvline(0, color='gray', linestyle='--', linewidth=1)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.axis("equal")
    limit = max(abs(x), abs(y)) + 0.5
    plt.xlim(-limit, limit)
    plt.ylim(-limit, limit)
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Gunshot DOA: Cartesian Plot")
    plt.legend()
    plt.savefig(os.path.join(PLOT_FOLDER, "cartesian.png"))  # Ensure correct path
    plt.close()



def process_wav_file(file_path):
    """Process WAV file: Extract features, compute DOA, and generate plots."""
    features = extract_features(file_path)
    if not features:
        return
    doa = calculate_doa(features["TDOA_1_2"], features["TDOA_1_3"], features["TDOA_1_4"])
    doa_rad = np.radians(doa)
    x = RADIUS * np.cos(doa_rad)
    y = RADIUS * np.sin(doa_rad)
    plot_polar(doa)
    plot_cartesian(x, y)
    # convert_xy_to_geo()
    return  doa_rad, x, y


def convert_xy_to_geo(mic_lat, mic_lon, x, y):
    """
    Convert (x, y) coordinates to latitude and longitude
    based on the microphone's geolocation.
    """
    mic_location = (mic_lat, mic_lon)

    # Calculate new latitude by moving "y" meters north/south
    new_lat = geodesic(meters=y).destination(mic_location, 0)[0]

    # Calculate new longitude by moving "x" meters east/west
    new_lon = geodesic(meters=x).destination(mic_location, 90)[1]

    return new_lat, new_lon


# -------------------------------------------------------------- Deployment Speciifc ----------------------------------------------------------------

import numpy as np
import matplotlib.pyplot as plt
import io
import os
from pymongo import MongoClient
import gridfs
from PIL import Image
# MongoDB Atlas connection
MONGO_URI = "mongodb+srv://root:root@bart-cluster.bal3tf2.mongodb.net/?retryWrites=true&w=majority&appName=BART-Cluster"  # Replace with your actual MongoDB Atlas URL
DB_NAME = "GunShot"  # Replace with your database name
COLLECTION_NAME = "polar_plots"
# Connect to MongoDB
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
plot_fs=gridfs.GridFS(db, collection="Plots")


def save_image_to_mongodb(image_data, filename):
    """Save image data to MongoDB using GridFS."""
    file_id = plot_fs.put(image_data, filename=filename, content_type="image/jpeg")
    print(f"Image saved to MongoDB with ID: {file_id}")
    return file_id

def reduce_image_size(image_bytes, quality=50):
    """Reduce image size using PIL and return bytes."""
    image = Image.open(io.BytesIO(image_bytes))
    image = image.convert("RGB")  # Ensure it's in RGB mode
    output = io.BytesIO()
    image.save(output, format="JPEG", quality=quality)  # Reduce quality
    return output.getvalue()

def upload_plot_polar(file_name ,doa):
    """Plot polar coordinates and save to MongoDB."""
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    doa_rad = np.radians(doa)
    ax.scatter(doa_rad, 1, color='b', label="Gunshot Direction")
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)
    ax.set_rticks([])
    ax.set_title("Polar Plot of DOA", va="bottom")
    ax.legend()

    # Save to a BytesIO buffer
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()

    # Reduce image size
    compressed_image = reduce_image_size(buf.getvalue())

    # Save to MongoDB
    return save_image_to_mongodb(compressed_image,file_name+"_polar_plot.jpg")

def upload_plot_cartesian(file_name,x, y):
    """Plot Cartesian coordinates and save to MongoDB."""
    plt.figure(figsize=(8, 8))
    plt.scatter(x, y, color='b', marker='o', label="Gunshot Location", s=100)
    plt.scatter(0, 0, color='r', marker='x', s=200, label="Microphone (Reference)")
    plt.axhline(0, color='gray', linestyle='--', linewidth=1)
    plt.axvline(0, color='gray', linestyle='--', linewidth=1)
    plt.grid(True, linestyle="--", linewidth=0.5)
    plt.axis("equal")
    limit = max(abs(x), abs(y)) + 0.5
    plt.xlim(-limit, limit)
    plt.ylim(-limit, limit)
    plt.xlabel("X Coordinate")
    plt.ylabel("Y Coordinate")
    plt.title("Gunshot DOA: Cartesian Plot")
    plt.legend()

    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()

    compressed_image = reduce_image_size(buf.getvalue())
    return save_image_to_mongodb(compressed_image,file_name+"_cartesian_plot.jpg")
