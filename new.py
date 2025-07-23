import csv
import numpy as np
from sklearn.metrics import euclidean_distances

def read_csv(file_path):
    """Read a CSV file and return the data as a list of rows."""
    try:
        with open(file_path, mode='r') as file:
            reader = csv.reader(file)
            return list(reader)
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {file_path} was not found.")
    except Exception as e:
        raise Exception(f"An error occurred while reading the file {file_path}: {e}")

def clean_data(data):
    """Ensure no NaN values in the input data and convert them to floats."""
    cleaned_data = []
    for value in data:
        try:
            cleaned_data.append(float(value))
        except ValueError:
            # Use a default value (0.0) for non-numeric or empty values
            cleaned_data.append(0.0)
    return cleaned_data

def calculate_distance(user_data, dress_data):
    """Calculate the Euclidean distance between user data and dress data."""
    if len(user_data) != len(dress_data):
        raise ValueError("User data and dress data must have the same number of dimensions.")
    
    return euclidean_distances([user_data], [dress_data]).flatten()[0]

def recommend_dresses(user_data, dresses_data):
    """Recommend top 5 dresses based on the user's measurements."""
    distances = []
    
    for dress_data in dresses_data:
        if len(dress_data) < 5 or dress_data[0] == 'image_name':
            # Skip rows with insufficient data or the header row
            continue
        
        image_name = dress_data[0]
        dress_measurements = np.array(clean_data(dress_data[1:]))  # Clean and convert measurements

        if len(user_data) != len(dress_measurements):
            # Ensure the user data and dress measurements have the same length
            continue
        
        distance = calculate_distance(user_data, dress_measurements)
        distances.append((image_name, distance, dress_data))
    
    # Sort by distance
    distances.sort(key=lambda x: x[1])

    # Save top recommendations to a CSV file with more details
    with open('recommended_dresses.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        # Write headers
        writer.writerow(['Rank', 'Image Name', 'Distance', 'Leg Length', 'Torso Length', 'Shoulder Width', 'Hip Width'])
        
        # Write top 5 recommendations with full details
        for i in range(min(5, len(distances))):
            image_name, distance, full_dress_data = distances[i]
            writer.writerow([
                i+1, 
                image_name, 
                f"{distance:.4f}", 
                full_dress_data[1],  # Leg Length
                full_dress_data[2],  # Torso Length
                full_dress_data[3],  # Shoulder Width
                full_dress_data[4]   # Hip Width
            ])

    print("Top 5 dress recommendations saved to 'recommended_dresses.csv'")
    
    # Return the top 5 recommendations with full details
    return [(image_name, distance, full_dress_data) for image_name, distance, full_dress_data in distances[:5]]

def load_and_process_data(user_csv, dresses_csv):
    """Load user and dress data from CSVs and generate recommendations."""
    user_data = read_csv(user_csv)
    dresses_data = read_csv(dresses_csv)

    if len(user_data) <= 1:
        raise ValueError("User data is empty or incorrectly formatted.")
    
    # Iterate through the user data to find valid measurements
    user_measurements = []
    for row in user_data[1:]:  # Skip the header row
        if row:  # Check if the row is not empty
            user_measurements = clean_data(row[1:])  # Clean and convert measurements
            if user_measurements and not all(m == 0.0 for m in user_measurements):
                break  # Found valid measurements, break out of the loop

    # Debugging: Print the cleaned user measurements
    print("Cleaned user measurements:", user_measurements)

    if len(user_measurements) == 0:
        raise ValueError("No valid user measurements found after cleaning.")

    top_5_dresses = recommend_dresses(user_measurements, dresses_data)
    return top_5_dresses

# Example Usage:
user_csv = 'measurements.csv'  # Path to the CSV containing the user's measurements
dresses_csv = 'Males_img_details.csv'  # Path to the CSV containing the dresses' measurements

try:
    top_5_dresses = load_and_process_data(user_csv, dresses_csv)
    print("\nTop 5 Recommendations:")
    for i, (image_name, distance, full_dress_data) in enumerate(top_5_dresses, 1):
        print(f"{i}. Image: {image_name}")
        print(f"   Distance: {distance:.4f}")
        print(f"   Dress Details: {full_dress_data}")
        print()
except Exception as e:
    print(f"An error occurred: {e}")