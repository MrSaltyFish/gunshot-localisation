from flask import Flask, render_template, request, send_from_directory
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
from doa_processor import process_wav_file

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
PLOT_FOLDER = 'static/plots'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PLOT_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part'
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)
    process_wav_file(file_path)  # Process file & generate plots
    return render_template('index.html', filename=file.filename)

@app.route('/plots/<filename>')
def get_plot(filename):
    return send_from_directory(PLOT_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
