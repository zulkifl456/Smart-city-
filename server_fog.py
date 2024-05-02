from flask import Flask, request, jsonify
import os
from werkzeug.utils import secure_filename
import cv2
import numpy as np

app = Flask(__name__)

# Directory where uploaded files will be stored
UPLOAD_FOLDER = r'C:\Users\FAJJOS\OneDrive\Desktop\Raspberry'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def calculate_brightness(image):
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    hist = cv2.calcHist([gray_image], [0], None, [256], [0, 256])
    cdf = hist.cumsum()
    cdf_normalized = cdf / cdf[-1]
    brightness_threshold = np.argmax(cdf_normalized > 0.5)
    brightness = np.mean(gray_image)
    return int(brightness), int(brightness_threshold)

def detect_flashlight_effect(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    # Normalize the grayscale image to enhance contrast differences
    normalized_gray = cv2.normalize(gray, None, alpha=0, beta=1, norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_32F)
    
    # Calculate the number of highly bright pixels
    bright_pixels = np.sum(normalized_gray > 0.9)  # Pixels that are extremely bright
    
    # Consider the ratio of bright pixels to the total number of pixels
    high_brightness_ratio = bright_pixels / gray.size

    # Adjust the threshold to be sensitive to flashlight effects
    if high_brightness_ratio > 0.09:  # More than 5% of the image is extremely bright
        return True
    return False

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(save_path)
        image = cv2.imread(save_path)

        brightness, brightness_threshold = calculate_brightness(image)
        fog_detected = detect_flashlight_effect(image)

        threshold = 100
        brightness_status = "dark" if brightness < threshold and brightness_threshold < threshold else "light"
        fog_status = "Foggy-Enviroment (flashlight detected)" if fog_detected else "No fog detected"
        
        print(f"Image '{filename}' brightness: {brightness}, threshold: {brightness_threshold}, status: {brightness_status}")
        print(f"Fog status: {fog_status}")

        return jsonify({
            "message": f"File {filename} uploaded successfully",
            "brightness": brightness,
            "brightness_threshold": brightness_threshold,
            "threshold": threshold,
            "status": brightness_status,
            "fog_status": fog_status
        }), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
