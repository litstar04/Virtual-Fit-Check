import cv2
import mediapipe as mp
import os
import math
import csv

# Initialize Mediapipe Pose model
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

def detect_landmarks(image_path):
    # Check if image file exists
    if not os.path.exists(image_path):
        print(f"Image not found: {image_path}")
        return None

    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Failed to load image: {image_path}")
        return None

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Process the image to find body landmarks
    results = pose.process(image_rgb)
    if results.pose_landmarks:
        return results.pose_landmarks.landmark
    else:
        print("No landmarks detected.")
        return None


def calculate_distance(point1, point2):
    # Calculate Euclidean distance between two points
    return math.sqrt(((point2.x - point1.x) ** 2) + ((point2.y - point1.y) ** 2))

def mid_point_distance(point1, point2, point3, point4):
    # Calculate the distance between midpoints of two sets of points
    mid_x1 = (point1.x + point2.x) / 2
    mid_y1 = (point1.y + point2.y) / 2
    mid_x2 = (point3.x + point4.x) / 2
    mid_y2 = (point3.y + point4.y) / 2
    mp_dist = math.sqrt(((mid_x1 - mid_x2) ** 2) + ((mid_y1 - mid_y2) ** 2))
    return mp_dist

def extract_measurements(landmarks, actual_height):
    # Define key points
    shoulder_left = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER]
    shoulder_right = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER]

    hip_left = landmarks[mp_pose.PoseLandmark.LEFT_HIP]
    hip_right = landmarks[mp_pose.PoseLandmark.RIGHT_HIP]

    # Defining nose height & factor
    nose = landmarks[mp_pose.PoseLandmark.NOSE]
    lfoot = landmarks[mp_pose.PoseLandmark.LEFT_FOOT_INDEX]
    rfoot = landmarks[mp_pose.PoseLandmark.RIGHT_FOOT_INDEX]

    nose_height = mid_point_distance(nose, nose, lfoot, rfoot)

    factor = (actual_height - 15) / nose_height
    print("factor : ", factor, "\n")
    print("height in cm : ", (nose_height * factor) + 10, "\n")
    print("height : ", actual_height, "\n")

    # Calculate measurements
    shoulder_width = calculate_distance(shoulder_left, shoulder_right)
    hip_width = calculate_distance(hip_left, hip_right)

    # Calculate leg_length , torso_length
    leg_length = mid_point_distance(hip_left, hip_right, lfoot, rfoot)
    torso_length = mid_point_distance(hip_left, hip_right, shoulder_left, shoulder_right)

    # Printing the results
    print("shoulder_width : ", (shoulder_width) * factor, "\n")
    print("hip_width : ", (hip_width) * factor, "\n")
    print("leg_length : ", (leg_length) * factor, "\n")
    print("torso_length : ", (torso_length) * factor, "\n")

    return [leg_length, torso_length, shoulder_width, hip_width]

def list_data(image_path, actual_height):
    landmarks = detect_landmarks(image_path)
    if landmarks:
        measurements = extract_measurements(landmarks, actual_height)
        return measurements
    return None

def user_input(file_path, actual_height, csv_file):
    # Open CSV file and append data
    with open(csv_file, 'a') as details:
        dataset = csv.writer(details)
        # Write header if the file is empty
        if os.path.getsize(csv_file) == 0:
            dataset.writerow(['image_name', 'leg_length', 'torso_length', 'shoulder_width', 'hip_width'])

        # Process the image and get measurements
        measurement = list_data(file_path, actual_height)
        if measurement:
            measurement.insert(0, file_path)
            dataset.writerow(measurement)
            print(measurement)

def main():
    actual_height = 180  # Replace with the user input for actual height

    # Directory paths for images
    men_dir = os.path.join('MPPS', 'MPPS', 'men')
    women_dir = os.path.join('MPPS', 'MPPS', 'women')

    # Process male images
    print("Processing Male Images...")
    for img in os.listdir(men_dir):
        file_path = os.path.join(men_dir, img)
        if os.path.exists(file_path):
            try:
                user_input(file_path, actual_height, 'Males_img_details.csv')
            except Exception as e:
                print(f"An error occurred while processing {img}: {e}")
        else:
            print(f"Image not found: {file_path}")

    # Process female images
    print("Processing Female Images...")
    for img in os.listdir(women_dir):
        file_path = os.path.join(women_dir, img)
        if os.path.exists(file_path):
            try:
                user_input(file_path, actual_height, 'Females_img_details.csv')
            except Exception as e:
                print(f"An error occurred while processing {img}: {e}")
        else:
            print(f"Image not found: {file_path}")

if __name__ == "__main__":
    main()
