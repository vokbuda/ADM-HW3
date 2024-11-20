import os
import pandas as pd

folder_path = "processed_files" #input files
locations = set()  #use a set to get unique combinations of restaurantName and City

#iterates through the files in the specified folder
for filename in os.listdir(folder_path):
    if filename.endswith(".tsv"):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path, sep='\t')
        
        #extract the restaurant name and city
        restaurant_name = df['restaurantName'].iloc[0] if 'restaurantName' in df.columns else None
        city = df['City'].iloc[0] if 'City' in df.columns else None
        
        #add only valid (not null) combinations to the set
        if restaurant_name and city:
            locations.add((restaurant_name, city))

# Crea un DataFrame con le combinazioni uniche di restaurantName e City
locations_df = pd.DataFrame(list(locations), columns=["restaurantName", "City"])
locations_df.to_csv("unique_locations.csv", index=False)
print("File 'unique_locations.csv' created with unique restaurant name and city combinations.")