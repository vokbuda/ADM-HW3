import pandas as pd
import time
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

#upload the city_to_region_final.csv file containing cities and regions
data = pd.read_csv("city_to_region_final.csv")

#initialize the geocoder
geolocator = Nominatim(user_agent="restaurant_mapper")

#function to get latitude and longitude
def get_coordinates(city, region):
    try:
        
        location = geolocator.geocode(f"{city}, {region}, Italy")
        if location:
            # Return latitude and longitude if found
            return location.latitude, location.longitude
    except GeocoderTimedOut:
        print(f"Geocoder timed out for {city}, {region}. Retrying...")
        time.sleep(1)
        
        return get_coordinates(city, region)
    #return None if coordinates are not found
    return None, None

#lists to store latitude and longitude
latitudes = []
longitudes = []
not_processed = []

#retrieve coordinates for each city
for index, row in data.iterrows():
    city = row['City']
    region = row['Region']
    print(f"({index + 1}/{len(data)}) Retrieving coordinates for: {city}, {region}")
    
    #get latitude and longitude
    lat, lon = get_coordinates(city, region)
    
    #check if coordinates were successfully retrieved
    if lat is not None and lon is not None:
        print(f"Coordinates found for {city}, {region}: ({lat}, {lon})")
    else:
        print(f"Failed to retrieve coordinates for {city}, {region}")
        #add city to not processed list if coordinates were not found
        not_processed.append(f"{city}, {region}")
    
    
    latitudes.append(lat)
    longitudes.append(lon)
    
    #pause to avoid overloading the server
    time.sleep(1)

#add coordinates to the DataFrame
data['latitude'] = latitudes
data['longitude'] = longitudes

#save the updated file with coordinates
data.to_csv("city_to_region_with_coordinates.csv", index=False)
print("File with coordinates saved as 'city_to_region_with_coordinates.csv'")

#aave the list of cities not processed correctly
with open("not_processed_cities.txt", "w") as f:
    for item in not_processed:
        f.write(f"{item}\n")
print("List of cities not processed correctly saved as 'not_processed_cities.txt'")