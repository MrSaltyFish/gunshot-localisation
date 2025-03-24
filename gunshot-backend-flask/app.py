from flask import Flask, jsonify
import joblib
import os

app = Flask(__name__)

PREDICTIONS_FILE = "predictions.joblib"

def load_predictions():
    if os.path.exists(PREDICTIONS_FILE):
        return joblib.load(PREDICTIONS_FILE)
    return {"error": "No predictions available"}

@app.route("/api/locate", methods=["GET"])
def get_prediction():
    data = load_predictions()
    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
