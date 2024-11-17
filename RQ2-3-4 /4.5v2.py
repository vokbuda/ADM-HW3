import os
import pandas as pd
import json
import math
import re
import heapq
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict
import folium

import nltk
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess_query(query):
    query = query.lower()
    query = re.sub(r'[^\w\s]', '', query)
    tokens = [stemmer.stem(word) for word in query.split() if word not in stop_words]
    return tokens

def load_index(vocab_file, index_file):
    vocab_df = pd.read_csv(vocab_file)
    vocabulary = dict(zip(vocab_df['term'], vocab_df['term_id'])) ##convert the vocabulary into a dictionary
    
    with open(index_file, 'r') as f:
        inverted_index = json.load(f)
        
    return vocabulary, inverted_index

def calculate_query_tfidf(query_terms, vocabulary, inverted_index, total_docs):
    query_tf = defaultdict(int)
    for term in query_terms:
        query_tf[term] += 1
    
    query_tfidf = {}
    norm_factor = 0
    for term, tf in query_tf.items():
        tf_value = tf / len(query_terms)
        idf_value = math.log(total_docs / (1 + len(inverted_index.get(term, []))))
        tfidf_score = tf_value * idf_value
        query_tfidf[term] = tfidf_score
        norm_factor += tfidf_score ** 2
    
    norm_factor = math.sqrt(norm_factor)
    for term in query_tfidf:
        query_tfidf[term] /= norm_factor if norm_factor > 0 else 1
    
    return query_tfidf

def cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector[term] * doc_vector.get(term, 0) for term in query_vector)
    query_norm = math.sqrt(sum(value ** 2 for value in query_vector.values()))
    doc_norm = math.sqrt(sum(value ** 2 for value in doc_vector.values()))
    if query_norm == 0 or doc_norm == 0:
        return 0.0
    return dot_product / (query_norm * doc_norm)

def execute_ranked_query(query, vocabulary, inverted_index, folder_path, total_docs, k):
    query_terms = preprocess_query(query)
    query_terms = [term for term in query_terms if term in inverted_index]
    if not query_terms:
        print("Nessun termine della query trovato nell'indice.")
        return pd.DataFrame()
    
    query_tfidf = calculate_query_tfidf(query_terms, vocabulary, inverted_index, total_docs)
    doc_scores = {}
    for term in query_terms:
        for doc_id, tfidf_score in inverted_index[term]:
            if doc_id not in doc_scores:
                doc_scores[doc_id] = defaultdict(float)
            doc_scores[doc_id][term] = tfidf_score
    
    results = []
    for doc_id, doc_vector in doc_scores.items():
        similarity = cosine_similarity(query_tfidf, doc_vector)
        if similarity > 0:
            results.append((doc_id, similarity))
    
    results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
    
    restaurant_results = [] #collect restaurant details
    for doc_id, score in results:
        file_path = os.path.join(folder_path, f"{doc_id}.tsv")
        df = pd.read_csv(file_path, sep='\t')
        restaurant_info = {
            "restaurantName": df['restaurantName'].iloc[0],
            "address": df['address'].iloc[0],
            "description": df['description'].iloc[0],
            "website": df['website'].iloc[0],
            "similarity_score": score
        }
        restaurant_results.append(restaurant_info)
    
    results_df = pd.DataFrame(restaurant_results, columns=["restaurantName", "address", "description", "website", "similarity_score"])
    return results_df

def custom_score(restaurant, description_score, query_terms):
    description_weight = 0.45
    cuisine_weight = 0.30
    facilities_weight = 0.05
    price_weight = 0.20

    score = description_score * description_weight

    cuisine_types = str(restaurant.get('cuisineType', '')).lower().split(',')
    cuisine_matches = sum(1 for term in query_terms if term in cuisine_types)
    if cuisine_matches > 0:
        score += (cuisine_matches / len(query_terms)) * cuisine_weight

    facilities = str(restaurant.get('facilitiesServices', '')).lower()
    facilities_matches = sum(1 for term in query_terms if term in facilities)
    if facilities_matches > 0:
        score += (facilities_matches / len(query_terms)) * facilities_weight

    #price preference keyword Lists
    cheap_terms = ["cheap", "affordable", "budget", "low-cost", "inexpensive", "economical", "reasonably priced"]
    moderate_terms = ["moderate", "average", "mid-range", "fair-priced", "decent"]
    expensive_terms = ["expensive", "premium", "high-end", "luxury", "upscale", "costly", "exclusive", "top-tier"]

    price_score = 0
    price = restaurant.get('priceRange', '')


    #scores restaurants based on the preferred price range in the query: 
    # cheap (‘€’, ‘€€’), moderate (‘€€’, ‘€€€’), or expensive (‘€€€’, ‘€€€€’) 
    # restaurants receive higher scores if they match the keywords in the query.
    if any(term in query_terms for term in cheap_terms):
        if '€' in price:
            price_score += 2
        elif '€€' in price:
            price_score += 1

    elif any(term in query_terms for term in moderate_terms):
        if '€€' in price or '€€€' in price:
            price_score += 2
        else:
            price_score += 1

    elif any(term in query_terms for term in expensive_terms):
        if '€€€' in price or '€€€€' in price:
            price_score += 2
        elif '€€' in price:
            price_score += 1

    #add the price score to the total score, weighted by the price weight
    score += price_score * price_weight


    return round(score, 2)

def execute_custom_ranked_query(query, vocabulary, inverted_index, folder_path, total_docs, k):
    base_results = execute_ranked_query(query, vocabulary, inverted_index, folder_path, total_docs, k)

    query_terms = preprocess_query(query)
    custom_results = []
    for _, row in base_results.iterrows():
        description_score = row["similarity_score"]
        restaurant = {
            "restaurantName": row["restaurantName"],
            "address": row["address"],
            "description": row["description"],
            "website": row["website"],
        }
        score = custom_score(restaurant, description_score, query_terms)
        restaurant["custom_score"] = score
        custom_results.append(restaurant)
    
    custom_results = sorted(custom_results, key=lambda x: x["custom_score"], reverse=True)[:k]
    custom_results_df = pd.DataFrame(custom_results, columns=["restaurantName", "address", "description", "website", "custom_score"])
    
    # Save results to CSV for mapping
    custom_results_df.to_csv("top_k_restaurants.csv", index=False)
    print("Top-K results saved to 'top_k_restaurants.csv'")
    
    return custom_results_df

def create_map(data):
    mappa = folium.Map(location=[41.8719, 12.5674], zoom_start=6) #create a map centered on Italy

    price_colors = {
        '€': 'green',
        '€€': 'blue',
        '€€€': 'orange',
        '€€€€': 'red'
    }
    #adds markers for each restaurant on the map
    for idx, row in data.iterrows():
        lat = row['latitude']
        lon = row['longitude']
        name = row['restaurantName']
        city = row['City']
        region = row['Region']
        price = row['priceRange']

        color = price_colors.get(price, 'gray') #default color if not found
        folium.Marker(
            location=[lat, lon],
            popup=f"<b>Restaurant:</b> {name}<br><b>City:</b> {city}<br><b>Region:</b> {region}<br><b>Price Range:</b> {price}",
            icon=folium.Icon(color=color) #use color based on price range
        ).add_to(mappa)


    #legend to interpret the colors of the price ranges
    legend_html = """
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 150px; height: 150px; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; padding: 10px;">
        <h4>Price Range Legend</h4>
        <i style="color:green">●</i> € - Inexpensive<br>
        <i style="color:blue">●</i> €€ - Moderate<br>
        <i style="color:orange">●</i> €€€ - Expensive<br>
        <i style="color:red">●</i> €€€€ - Very Expensive
    </div>
    """
    mappa.get_root().html.add_child(folium.Element(legend_html)) #adds legend to map
    
    mappa.save("italy_restaurant_map_with_legend.html") #save the map to an HTML file
    print("Map created and saved as 'italy_restaurant_map_with_legend.html'")

if __name__ == "__main__":
    vocab_file = "vocabulary.csv"
    index_file = "tfidf_inverted_index.json"
    folder_path = "processed_files"
    
    vocabulary, inverted_index = load_index(vocab_file, index_file)
    total_docs = len(os.listdir(folder_path))
    
    query = input("Inserisci la tua query: ")
    k = int(input("Inserisci il numero di risultati top-k da visualizzare: "))
    
    #gets the most relevant restaurant data and merges it with price and coordinate data
    top_k_data = execute_custom_ranked_query(query, vocabulary, inverted_index, folder_path, total_docs, k)
    
    additional_data = pd.read_csv("city_to_region_with_prices.csv")
    merged_data = pd.merge(top_k_data, additional_data, on="restaurantName", how="left")
    
    create_map(merged_data) #create the map with filtered restaurants and view the details