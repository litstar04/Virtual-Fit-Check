import pandas as pd

# Load the original dataset
clothing_num_data = pd.read_csv('img_details.csv')

# Separate male and female datasets
male_data = clothing_num_data[clothing_num_data['Gender'] == 'Male']
female_data = clothing_num_data[clothing_num_data['Gender'] == 'Female']

# Save them as separate CSV files
male_data.to_csv('male.csv', index=False)
female_data.to_csv('female.csv', index=False)

print("Male and Female datasets created successfully.")