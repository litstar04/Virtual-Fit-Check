import pandas as pd
import os
import json


def get_user_gender():
    session_file = "user_session.json"
    
    # Check if session file exists, if not, return default "Male"
    if not os.path.exists(session_file):
        # print("Error: 'user_session.json' file not found.")
        return "Male"  \
    
    # Load session data from the file
    with open(session_file, "r") as file:
        user_session = json.load(file)
    return user_session.get("gender", "Male")

user_gender = get_user_gender()
print(user_gender)
csv_file = "euclid_recommends.csv" 
df = pd.read_csv(csv_file)

image_folder_men = "MPPS/MPPS/men"
image_folder_women = "MPPS/MPPS/women"

if user_gender == "Male":
    image_folder = image_folder_men
elif user_gender == "Female":
    image_folder = image_folder_women
else:
    image_folder = image_folder_women  

matched_images = []

for image_name in df['image_name']:
    clean_image_name = image_name.replace("MPPS\\MPPS\\men\\", "").replace("MPPS\\MPPS\\women\\", "")  
    image_path = os.path.join(image_folder, clean_image_name)
    
    if os.path.exists(image_path):
        matched_images.append(image_path)

if not matched_images:
    print("No matching images found.")
    exit()

html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Image Gallery</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 20px;
        }
        h1 {
            color: #333;
        }
        img {
            max-width: 200px;
            margin: 10px;
            border: 1px solid #ccc;
            border-radius: 5px;
        }
        .gallery {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 15px;
        }
    </style>
</head>
<body>
    <h1>Image Gallery</h1>
    <div class="gallery">
"""

# Loop to add image tags dynamically
for image_path in matched_images:
    # Get relative path for the server
    relative_path = os.path.relpath(image_path, start=os.getcwd())
    # Add the image HTML to the content
    html_content += f'<img src="{relative_path}" alt="{os.path.basename(image_path)}">\n'

# Close the HTML structure
html_content += """
    </div>
</body>
</html>
"""

# Write the HTML content to a file
with open("image_recommendations.html", "w") as html_file:
    html_file.write(html_content)

print("HTML file generated: image_recommendations.html")