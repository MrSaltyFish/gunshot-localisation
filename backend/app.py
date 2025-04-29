# from flask import Flask, request, render_template, jsonify, send_file
# from flask_cors import CORS
# import os
# from dotenv import load_dotenv
# import numpy as np
# from io import BytesIO
# from doa_processor import extract_features, calculate_doa, plot_polar, plot_cartesian, convert_xy_to_geo
# from database import save_audio_to_db, fetch_file

# # Initialize Flask App
# print("Looking for templates in:", os.path.abspath("../frontend/templates"))
# app = Flask(__name__)
# CORS(app)  # Allow frontend requests

# # Ensure 'uploads' directory exists
# UPLOAD_FOLDER = "uploads"
# os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# @app.route("/")
# def index():
#     return render_template("index.html")

# @app.route("/fetch_plot/<filename>")
# def fetch_plot(filename):
#     try:
#         plot_file = fetch_file(filename)
#         return send_file(BytesIO(plot_file.read()), mimetype="image/png")
#     except Exception as e:
#         return jsonify({"error": f"Plot not found: {str(e)}"}), 404

# @app.route("/upload", methods=["POST"])
# def upload_file():
#     if "file" not in request.files:
#         print("🚨 error = No file uploaded")
#         return jsonify({"error - No file uploaded"}), 404

#     file = request.files["file"]
#     mic_coords_str = request.form.get("mic_coords", "0,0")  # Default to "0,0" if not provided
#     mic_coords = mic_coords_str.split(",")

#     if file.filename == "":
#         print("🚨 No file uploaded in the request")
#         return jsonify({"error - File Name is Empty"}), 400
    
#     # Save file to MongoDB
#     file_data = file.read()
#     file_id = save_audio_to_db(file.filename, file_data)

#     # Save file temporarily in backend/uploads/
#     temp_file_path = os.path.join(UPLOAD_FOLDER, file.filename)
#     with open(temp_file_path, "wb") as f:
#         f.write(file_data)

#     # Extract TDOA features
#     tdoa_values = extract_features(temp_file_path)
#     if tdoa_values is None or len(tdoa_values) < 3:
#         return jsonify({"error - Invalid file or insufficient TDOA values"}), 400

#     # Compute DOA (Fix: Access list indices correctly)
#     doa = calculate_doa(tdoa_values[0], tdoa_values[1], tdoa_values[2])
#     doa_rad = np.radians(doa)
#     x = np.cos(doa_rad)
#     y = np.sin(doa_rad)

#     # Convert (x, y) to latitude/longitude
#     gunshot_lat, gunshot_lon = convert_xy_to_geo(float(mic_coords[0]), float(mic_coords[1]), x, y)

#     # Generate Plots
#     polar_plot = plot_polar(doa)
#     cartesian_plot = plot_cartesian(x, y)

#     return jsonify({
#         "filename": file.filename,
#         "doa_rad": float(doa_rad),
#         "x": float(x),
#         "y": float(y),
#         "gunshot_lat": float(gunshot_lat),
#         "gunshot_long": float(gunshot_lon),
#         "polar_plot": polar_plot,
#         "cartesian_plot": cartesian_plot
#     })

# if __name__ == "__main__":
#     app.run(debug=True, port=5000)

from flask import Flask, request, render_template, jsonify, send_file ,send_from_directory, Response # type: ignore
from flask_cors import CORS  # type: ignore
import os
from dotenv import load_dotenv # type: ignore
import numpy as np # type: ignore
from io import BytesIO
from doa_processor import extract_features, calculate_doa, plot_polar, plot_cartesian, convert_xy_to_geo , upload_plot_cartesian , upload_plot_polar
from database import save_audio_to_db, fetch_file , save_audio_to_audio_collection , fetch_plots , fetch_plots_new
from bson import ObjectId
file_name=""
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Initialize Flask App
print("Looking for templates in:", os.path.abspath("../backend/templates"))
app = Flask(__name__, static_folder="../backend/static", static_url_path="")
CORS(app)  # Enable CORS for frontend-backend communication

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')  # Change path if needed
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure folder exists

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route("/", methods=["GET", "POST"])
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

# @app.route("/fetch_plot/<filename>")
# def fetch_plot(filename):
#     try:
#         plot_file = fetch_file(filename+"_polar_plot.jpg")
#         return send_file(BytesIO(plot_file.read()), mimetype="image/jpeg")
#     except Exception as e:
#         return jsonify({"error": f"Plot not found: {str(e)}"}), 404



@app.route("/upload", methods=["POST"])
def upload_file():
    if "file" not in request.files:
        print("🚨 error = No file uploaded")
        return jsonify({"error": "No file uploaded"}), 404

    file = request.files["file"]
    mic_coords_str = request.form.get("mic_coords", "0,0")  # Default to "0,0" if not provided
    mic_coords = [float(coord) for coord in mic_coords_str.split(",")]

    if file.filename == "":
        print("🚨 No file uploaded in the request")
        return jsonify({"error": "File Name is Empty"}), 400
    
    # Save file to MongoDB
    file_data = file.read()
    global file_name
    file_name = file.filename
    file_id = save_audio_to_audio_collection(file.filename, file_data)
    
    # Save file temporarily in backend/uploads/
    temp_file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    with open(temp_file_path, "wb") as f:
        f.write(file_data)

    # Extract TDOA features
    features = extract_features(temp_file_path)
    if features is None:
        return jsonify({"error": "Invalid file or insufficient TDOA values"}), 400

    # Compute DOA
    doa = calculate_doa(features["TDOA_1_2"], features["TDOA_1_3"], features["TDOA_1_4"])
    doa_rad = np.radians(doa)
    x = np.cos(doa_rad)
    y = np.sin(doa_rad)

    # Convert (x, y) to latitude/longitude
    gunshot_lat, gunshot_lon = convert_xy_to_geo(mic_coords[0], mic_coords[1], x, y)

    # Generate Plots
    obj_id_polar = upload_plot_polar(file_name,doa)
    obj_id_cartesian = upload_plot_cartesian(file_name,x, y)

    # polar_plot_data = fetch_plots_new(obj_id_polar)
    # cartesian_plot_data = fetch_plots_new(obj_id_cartesian)

    # # Debugging prints
    # print('*' * 50)
    # print("Polar Plot Data:", polar_plot_data)
    # print("Cartesian Plot Data:", cartesian_plot_data)
    # print('*' * 50)

    polar_plot_data = fetch_plots_new(obj_id_polar).json.get("image")
    cartesian_plot_data = fetch_plots_new(obj_id_cartesian).json.get("image")

    return jsonify({
        "filename": file.filename,
        "doa_rad": float(doa_rad),
        "x": float(x),
        "y": float(y),
        "gunshot_lat": float(gunshot_lat),
        "gunshot_long": float(gunshot_lon),
        "cartesian_plot_image": cartesian_plot_data,
        "polar_plot_image": polar_plot_data
    }), 200
# # fetch from the DB
# @app.route("/get_image/<file_id>", methods=["GET"])
# def get_image(file_id):
#     try:
#         # Convert string ID to ObjectId
#         obj_id = ObjectId(file_id)
        
#         # Retrieve file from GridFS
#         file_data = fs.get(obj_id)

#         # Return the image with appropriate MIME type
#         return Response(file_data.read(), content_type="image/png")
    
#     except Exception as e:
#         return {"error": str(e)}, 404  # Return an error if not found

if __name__ == "__main__":
    app.run(debug=True, port=5000)
