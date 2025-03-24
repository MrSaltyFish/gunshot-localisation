import pickle

data = {
    "DOA": "45 degrees",
    "TDOA": "2.3 ms",
    "Gun Type": "9mm Pistol",
    "Location": {"latitude": 40.7128, "longitude": -74.0060}
}

with open("predictions.pkl", "wb") as f:
    pickle.dump(data, f)

print("Saved predictions to predictions.pkl")
