from flask import Flask, jsonify
import pickle
import os

app = Flask(__name__)

# Load the model output (Assume we have some precomputed results)
PREDICTIONS_FILE = "predictions.pkl"

def load_predictions():
    if os.path.exists(PREDICTIONS_FILE):
        with open(PREDICTIONS_FILE, "rb") as f:
            return pickle.load(f)
    return {"error": "No predictions available"}

@app.route("/api/locate", methods=["GET"])
def get_prediction():
    data = load_predictions()
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
