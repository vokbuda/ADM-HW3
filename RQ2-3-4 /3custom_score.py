import os
import pandas as pd
import json
import math
import re
import heapq
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict

import nltk
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

#preprocess la query
def preprocess_query(query):
    query = query.lower()
    query = re.sub(r'[^\w\s]', '', query)
    tokens = [stemmer.stem(word) for word in query.split() if word not in stop_words]
    return tokens

def load_index(vocab_file, index_file):
    vocab_df = pd.read_csv(vocab_file)
    vocabulary = dict(zip(vocab_df['term'], vocab_df['term_id'])) #convert the vocabulary into a dictionary
    
    with open(index_file, 'r') as f:
        inverted_index = json.load(f)
        
    return vocabulary, inverted_index

def execute_conjunctive_query(query, vocabulary, inverted_index, folder_path):
    query_terms = preprocess_query(query)
    term_ids = [vocabulary.get(term) for term in query_terms if term in vocabulary]
    term_ids = [term_id for term_id in term_ids if term_id is not None]
    
    if not term_ids:
        print("No query terms found in the vocabulary.")
        return []

    doc_sets = [set(inverted_index[str(term_id)]) for term_id in term_ids if str(term_id) in inverted_index]
    common_docs = set.intersection(*doc_sets) if doc_sets else set()
    
    results = [] #collect restaurant details 
    for doc_id in common_docs:
        file_path = os.path.join(folder_path, f"{doc_id}.tsv")
        df = pd.read_csv(file_path, sep='\t')
        restaurant_info = {
            "restaurantName": df['restaurantName'].iloc[0],
            "address": df['address'].iloc[0],
            "description": df['description'].iloc[0],
            "website": df['website'].iloc[0],
            "doc_id": doc_id
        }
        results.append(restaurant_info)
    return results

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
        print("No query terms found in index.")
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
    #sort results by similarity and return top-k
    results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
    
    restaurant_results = []
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
    description_weight = 0.45 #weight for description
    cuisine_weight = 0.30 #weight for the type of cuisine
    facilities_weight = 0.05 #weight for services
    price_weight = 0.20 #weight for the price range

    #initialize the score with the description similarity
    score = description_score * description_weight

    #added score for cuisine type
    cuisine_types = str(restaurant.get('cuisineType', '')).lower().split(',')
    cuisine_matches = sum(1 for term in query_terms if term in cuisine_types)
    if cuisine_matches > 0:
        score += (cuisine_matches / len(query_terms)) * cuisine_weight

    #added score for services
    facilities = str(restaurant.get('facilitiesServices', '')).lower()
    facilities_matches = sum(1 for term in query_terms if term in facilities)
    if facilities_matches > 0:
        score += (facilities_matches / len(query_terms)) * facilities_weight

    #price Preference Keyword Lists
    cheap_terms = ["cheap", "affordable", "budget", "low-cost", "inexpensive", "economical", "reasonably priced"]
    moderate_terms = ["moderate", "average", "mid-range", "fair-priced", "decent"]
    expensive_terms = ["expensive", "premium", "high-end", "luxury", "upscale", "costly", "exclusive", "top-tier"]

    #price range score based on query preferences
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
    for _, row in base_results.iterrows(): #iterate through each base_results
        description_score = row["similarity_score"] #collect restaurant information from each base_results row
        restaurant = {
            "restaurantName": row["restaurantName"],
            "address": row["address"],
            "description": row["description"],
            "website": row["website"],
            "priceRange": row.get("priceRange", ""),
            "cuisineType": row.get("cuisineType", ""),
            "facilitiesServices": row.get("facilitiesServices", "")
        }
        score = custom_score(restaurant, description_score, query_terms) #calculate the personalized restaurant score
        restaurant["custom_score"] = score
        custom_results.append(restaurant)
    
    custom_results = sorted(custom_results, key=lambda x: x["custom_score"], reverse=True)[:k] #keep only the first k results
    return pd.DataFrame(custom_results, columns=["restaurantName", "address", "description", "website", "custom_score"])

if __name__ == "__main__":
    vocab_file = "vocabulary.csv"
    index_file = "tfidf_inverted_index.json"
    folder_path = "processed_files"
    
    vocabulary, inverted_index = load_index(vocab_file, index_file)
    total_docs = len(os.listdir(folder_path))
    
    query = input("Enter your query: ")
    k = int(input("Enter the number of top-k results to display: "))
    results_df = execute_custom_ranked_query(query, vocabulary, inverted_index, folder_path, total_docs, k)
    
    if not results_df.empty:
        print(results_df)
        results_df.to_csv("top_k_restaurants.csv", index=False) #For RQ4
        print("Results saved in 'top_k_restaurants.csv'")
    else:
        print("No results found for the given query.")




'''
The results of the two codes are different because they use different approaches.

The first method (RQ2.2.2) is simpler and is based only on restaurant descriptions. 
This makes it very precise when the query terms are present in the descriptions, but it does not take into account other aspects.

The second method (RQ3), on the other hand, is more complete because it also considers other factors, 
such as price, services and type of cuisine.
This makes it more useful for those who have more specific preferences or want a more personalized result.

The first method is based only on the matching of the terms in the description, so it is simple but can be limited.
The second method also considers other aspects such as price, services and type of cuisine, providing more complete results. 
However, it may penalize restaurants with very relevant descriptions if they do not meet other criteria of the query.
'''