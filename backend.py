import os
import csv
import math
import mediapipe as mp
import base64
import numpy as np
from flask import Flask, request, jsonify
from flask_cors import CORS
import cv2

app = Flask(__name__)
CORS(app)
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Helper function to calculate distance between points
def calculate_distance(point1, point2):
    return math.sqrt(((point2.x - point1.x) ** 2) + ((point2.y - point1.y) ** 2))

# Function to convert base64 image string to an OpenCV image
def base64_to_image(base64_str):
    img_data = base64.b64decode(base64_str.split(',')[1])
    np_arr = np.frombuffer(img_data, np.uint8)
    img_np = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
    if img_np is None:
        print("Image decoding failed.")
    else:
        print("Image decoded successfully. Shape:", img_np.shape)
    return img_np

# Function to extract measurements from landmarks
def extract_measurements(landmarks, actual_height):
    VISIBILITY_THRESHOLD = 0.3  # Visibility threshold
    
    # Extract key landmarks
    shoulder_left = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    shoulder_right = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]
    hip_left = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    hip_right = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]
    nose = landmarks[mp_pose.PoseLandmark.NOSE]
    lfoot = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
    rfoot = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]

    # Check visibility of key landmarks
    if (shoulder_left.visibility < VISIBILITY_THRESHOLD or 
        shoulder_right.visibility < VISIBILITY_THRESHOLD or 
        hip_left.visibility < VISIBILITY_THRESHOLD or 
        hip_right.visibility < VISIBILITY_THRESHOLD or 
        nose.visibility < VISIBILITY_THRESHOLD or 
        lfoot.visibility < VISIBILITY_THRESHOLD or 
        rfoot.visibility < VISIBILITY_THRESHOLD):
        print("Some key landmarks have low visibility.")
        return None

    # Calculate measurements based on detected landmarks
    nose_height = calculate_distance(nose, lfoot)  # Simplified distance calculation
    factor = (actual_height - 10) / nose_height
    
    shoulder_width = calculate_distance(shoulder_left, shoulder_right) * factor
    hip_width = calculate_distance(hip_left, hip_right) * factor
    leg_length = calculate_distance(hip_left, lfoot) * factor
    torso_length = calculate_distance(shoulder_left, hip_left) * factor
    
    return [leg_length, torso_length, shoulder_width, hip_width]

# Function to save measurements to CSV
def save_to_csv(data):
    csv_path = 'measurements.csv'

    print(f"Saving data to CSV at path: {csv_path}")

    # Open the CSV file and append data
    with open(csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        # Write header if file is empty
        if os.path.getsize(csv_path) == 0:
            print("CSV file is empty, writing header row.")
            writer.writerow(['Height', 'Torso Length', 'Leg Length', 'Shoulder Width', 'Hip Width'])
        
        # Write the measurements data to the file
        writer.writerow([data['height'], data['torso_length'], data['leg_length'], data['shoulder_width'], data['hip_width']])

# Endpoint to process image and return measurements
@app.route('/measure', methods=['POST'])
def measure():
    try:
        data = request.get_json()
        
        if 'image_data' not in data:
            return jsonify({"error": "No image data provided"}), 400

        img_np_format = base64_to_image(data['image_data'])
        
        # Process the image for pose landmarks
        results = pose.process(cv2.cvtColor(img_np_format, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            actual_height = 163  # Replace with user input if needed
            measurements = extract_measurements(results.pose_landmarks.landmark, actual_height)

            if measurements is None:
                return jsonify({"error": "Some key landmarks have low visibility."}), 400

            # Save measurements to CSV
            save_to_csv({
                'height': actual_height,
                'torso_length': measurements[1],
                'leg_length': measurements[0],
                'shoulder_width': measurements[2],
                'hip_width': measurements[3],
            })

            return jsonify({
                "message": "Automatic measurements saved successfully",
                "measurements": {
                    "leg_length": measurements[0],
                    "torso_length": measurements[1],
                    "shoulder_width": measurements[2],
                    "hip_width": measurements[3],
                }
            }), 200

        else:
            return jsonify({"error": "No landmarks detected."}), 400

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

# Endpoint to accept manual measurements from the user
@app.route('/manual_measurements', methods=['POST'])
def manual_measurements():
    try:
        data = request.get_json()
        
        # Ensure 'height' is provided in the data
        if 'height' not in data:
            return jsonify({"error": "Height is required."}), 400

        height = float(data['height'])  # Parse height as a float

        # Manually calculate measurements based on height
        torso_length = 0.3 * height
        leg_length = 0.5 * height
        shoulder_width = 0.2 * height
        hip_width = 0.18 * height

        # Save measurements to CSV
        save_to_csv({
            'height': height,
            'torso_length': torso_length,
            'leg_length': leg_length,
            'shoulder_width': shoulder_width,
            'hip_width': hip_width,
        })

        return jsonify({
            "message": "Manual measurements saved successfully",
            "measurements": {
                "torso_length": torso_length,
                "leg_length": leg_length,
                "shoulder_width": shoulder_width,
                "hip_width": hip_width,
            }
        }), 200

    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500
# @app.route('/recommendations', methods=['GET'])
# def recommendations():
#     # Just an example to show that we can render this page
#     return render_template('recommendations.html')

# Basic index route to check if the backend is running
@app.route('/')
def index():
    return "Backend is running! Available endpoints: /manual_measurements and /measure"

# Start the Flask app
if __name__ == '__main__':
   with app.test_request_context():
       print(app.url_map)
   app.run(debug=True)
