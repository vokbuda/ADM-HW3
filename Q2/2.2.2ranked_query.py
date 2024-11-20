import os
import pandas as pd
import json
import math
import re
from tabulate import tabulate  # Libreria per visualizzare i dati come tabella
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict

import nltk
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess_query(query):
    query = query.lower()
    query = re.sub(r'[^\w\s]', '', query)
    tokens = [stemmer.stem(word) for word in query.split() if word not in stop_words]
    return tokens

# Calculate TF-IDF vector for query terms
def calculate_query_tfidf(query_terms, vocabulary, inverted_index, total_docs):
    query_tf = defaultdict(int)
    for term in query_terms:
        query_tf[term] += 1
    
    query_tfidf = {}
    norm_factor = 0  # Normalization factor for query vector
    for term, tf in query_tf.items():
        # TF for query
        tf_value = tf / len(query_terms)
        # IDF for query
        idf_value = math.log(total_docs / (1 + len(inverted_index.get(term, []))))
        tfidf_score = tf_value * idf_value
        query_tfidf[term] = tfidf_score
        norm_factor += tfidf_score ** 2 
    # Vector normalization
    norm_factor = math.sqrt(norm_factor)
    for term in query_tfidf:
        query_tfidf[term] /= norm_factor if norm_factor > 0 else 1
    
    return query_tfidf

# Calculate the cosine similarity between the query vector and a document vector
def cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector[term] * doc_vector.get(term, 0) for term in query_vector)
    query_norm = math.sqrt(sum(value ** 2 for value in query_vector.values()))
    doc_norm = math.sqrt(sum(value ** 2 for value in doc_vector.values()))
    if query_norm == 0 or doc_norm == 0:
        return 0.0
    return dot_product / (query_norm * doc_norm)

def execute_ranked_query(query, vocabulary, inverted_index, folder_path, total_docs, k):
    # Preprocess la query
    query_terms = preprocess_query(query)
    print(f"Query terms after preprocessing: {query_terms}")
    
    # Filter terms not present in the index
    query_terms = [term for term in query_terms if term in inverted_index]
    if not query_terms:
        print("No query terms found in index.")
        return pd.DataFrame()
    
    # Calculate the vector TF-IDF for query
    query_tfidf = calculate_query_tfidf(query_terms, vocabulary, inverted_index, total_docs)
    print(f"TF-IDF vector of the query (normalized): {query_tfidf}")
    
    # Calculate the cosine similarity for each document that contains at least one query term
    doc_scores = {}
    for term in query_terms:
        for doc_id, tfidf_score in inverted_index[term]:
            if doc_id not in doc_scores:
                doc_scores[doc_id] = defaultdict(float)
            doc_scores[doc_id][term] = tfidf_score
    
    # Calculate the cosine similarity between the query and each document
    results = []
    for doc_id, doc_vector in doc_scores.items():
        similarity = cosine_similarity(query_tfidf, doc_vector)
        if similarity > 0:
            results.append((doc_id, similarity))
            print(f"Document: {doc_id}, Similarity: {similarity}")
    
    # Sort results by similarity and return top-k
    results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
    
    # Collect restaurant details for found doc_ids
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
    
    # Creating the results DataFrame
    results_df = pd.DataFrame(restaurant_results, columns=["restaurantName", "address", "description", "website", "similarity_score"])
    return results_df

if __name__ == "__main__":
    
    vocab_file = "vocabulary.csv"  # Vocabulary path
    index_file = "tfidf_inverted_index.json"  # Inverted index with TF-IDF path
    folder_path = "processed_files"  # Input files
    
    # Load vocabulary and index inverted
    with open(index_file, 'r') as f:
        inverted_index = json.load(f)
    total_docs = len(os.listdir(folder_path))
    
    # Prompts the user for the query
    query = input("Enter your query: ")
    k = int(input("Enter the number of top-k results to display: "))
    results_df = execute_ranked_query(query, None, inverted_index, folder_path, total_docs, k)
    
    # Show results
    if not results_df.empty:
        # Display the results as a formatted table
        print(tabulate(results_df, headers="keys", tablefmt="grid", showindex=False))
    else:
        print("No results found for the given query.")