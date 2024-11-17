import os
import pandas as pd
import json
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

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
    vocabulary = dict(zip(vocab_df['term'], vocab_df['term_id']))
    
    with open(index_file, 'r') as f:
        inverted_index = json.load(f)
        
    return vocabulary, inverted_index

def execute_conjunctive_query(query, vocabulary, inverted_index, folder_path):
    #preprocess the query
    query_terms = preprocess_query(query)
    print(f"Query terms after preprocessing: {query_terms}")
    
    #find the term_ids for each query term
    term_ids = [vocabulary.get(term) for term in query_terms if term in vocabulary]
    term_ids = [term_id for term_id in term_ids if term_id is not None]
    print(f"term_id found in query: {term_ids}")
    
    if not term_ids:
        print("No query terms found in the vocabulary.")
        return []

    #find doc_ids that contain all term_ids
    doc_sets = [set(inverted_index[str(term_id)]) for term_id in term_ids if str(term_id) in inverted_index]
    common_docs = set.intersection(*doc_sets) if doc_sets else set()
    print(f"doc_id comuni trovati: {common_docs}")
    
    #collect restaurant details for found doc_ids
    results = []
    for doc_id in common_docs:
        file_path = os.path.join(folder_path, f"{doc_id}.tsv")
        df = pd.read_csv(file_path, sep='\t')
        restaurant_info = {
            "restaurantName": df['restaurantName'].iloc[0],
            "address": df['address'].iloc[0],
            "description": df['description'].iloc[0],
            "website": df['website'].iloc[0]
        }
        results.append(restaurant_info)
    
    #creating the results DataFrame
    results_df = pd.DataFrame(results, columns=["restaurantName", "address", "description", "website"])
    return results_df

if __name__ == "__main__":
    vocab_file = "vocabulary.csv"  #vocabulary path
    index_file = "inverted_index.json"  #inverted index path
    folder_path = "processed_files" 
    
    vocabulary, inverted_index = load_index(vocab_file, index_file)
    
    #prompts the user for the query
    query = input("Enter your query: ")
    results_df = execute_conjunctive_query(query, vocabulary, inverted_index, folder_path)
    
    #show results
    if not results_df.empty:
        print(results_df)
    else:
        print("No results found for the given query.")