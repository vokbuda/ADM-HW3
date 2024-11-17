import os
import pandas as pd
import requests
import time

#load unique cities from the file `unique_locations.csv`
cities_df = pd.read_csv("unique_locations.csv")
cities_df["Region"] = ""  #empty column to save the region

#list for cities not found
not_found = []

#function to get the region using the Nominatim API
def get_region(city, country="Italy"):
    url = "https://nominatim.openstreetmap.org/search" #URL and parameters for the API request
    params = {
        'q': f"{city}, {country}",
        'format': 'json',
        'addressdetails': 1,
        'limit': 1
    }
    headers = {'User-Agent': 'ADMHW3'} #request header to identify yourself, without this the code gave errors.
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200 and response.json():
            address = response.json()[0].get('address', {})
            return address.get('state') #gets the name of the region
    except requests.exceptions.RequestException as e:
        print(f"Connection error for {city}: {e}")
    return None

#counter to track the number of requests and errors
error_count = 0
processed_count = 0

#iterate through the cities and retrieve their regions
for idx, row in cities_df.iterrows():
    city = row['City']
    print(f"({idx+1}/{len(cities_df)}) Retrieving region for: {city}")
    region = None
    for attempt in range(2):  #attempt to get the region up to 2 times
        region = get_region(city)
        if region: #if the region is found it saves it in the "Region" column
            cities_df.at[idx, "Region"] = region
            print(f"Region found for {city}: {region}")
            error_count = 0  
            break
        else: #if the attempt fails, print a message and wait before trying again
            print(f"Attempt {attempt + 1} failed for {city}. Retrying...")
            time.sleep(10 * (attempt + 1)) 

    if not region: #if after attempts the region is not found, add the city to the "not_found" list
        print(f"Region not found for: {city}")
        not_found.append(city)

    processed_count += 1

    #periodic save every 100 cities
    if processed_count % 100 == 0:
        cities_df.to_csv("city_to_region_partial.csv", index=False)
        with open("not_found_cities.txt", "w") as f:
            for nf_city in not_found:
                f.write(f"{nf_city}\n")
        print("Periodic save completed every 100 cities.")

    #extended pause every 100 requests
    if processed_count % 100 == 0:
        print("Extended pause of 120 seconds every 100 requests.")
        time.sleep(120)

    #10 second pause between each request
    time.sleep(10)

#final save of the results
cities_df.to_csv("city_to_region_final.csv", index=False)
with open("not_found_cities.txt", "w") as f:
    for city in not_found:
        f.write(f"{city}\n")

print("Process completed. Final results saved in 'city_to_region_final.csv' and 'not_found_cities.txt'")