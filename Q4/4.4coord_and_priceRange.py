import os
import pandas as pd

##upload the file with cities, regions and coordinates
data = pd.read_csv("city_to_region_with_coordinates.csv")
folder_path = "restaurants_tsv"

price_dict = {} #dictionary to map restaurant names to price range
for filename in os.listdir(folder_path):
    if filename.endswith(".tsv"):
        file_path = os.path.join(folder_path, filename)
        df = pd.read_csv(file_path, sep='\t')

        #check that the required columns exist in the file
        if 'restaurantName' in df.columns and 'priceRange' in df.columns:
            #adds the restaurant name as key and the price range as value
            price_dict[df['restaurantName'][0]] = df['priceRange'][0]

data['priceRange'] = data['restaurantName'].map(price_dict) #adds a new column 'priceRange'
data.to_csv("city_to_region_with_prices.csv", index=False) #save the updated file
print("File 'city_to_region_with_prices.csv' updated with price ranges.")