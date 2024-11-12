import os
import pandas as pd
import json
import math
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from collections import defaultdict

# Assicuriamoci che le risorse di nltk siano disponibili
import nltk
nltk.download('stopwords')

# Definizione della lista delle stopword e dello stemmer
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess_query(query):
    # Converti in minuscolo, rimuovi punteggiatura e applica stemming
    query = query.lower()
    query = re.sub(r'[^\w\s]', '', query)
    tokens = [stemmer.stem(word) for word in query.split() if word not in stop_words]
    return tokens

def calculate_query_tfidf(query_terms, vocabulary, inverted_index, total_docs):
    query_tf = defaultdict(int)
    for term in query_terms:
        query_tf[term] += 1
    
    query_tfidf = {}
    for term, tf in query_tf.items():
        # TF per la query
        tf_value = tf / len(query_terms)
        # IDF per la query
        idf_value = math.log(total_docs / (1 + len(inverted_index.get(term, []))))
        query_tfidf[term] = tf_value * idf_value
    
    return query_tfidf

def cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector[term] * doc_vector.get(term, 0) for term in query_vector)
    query_norm = math.sqrt(sum(value ** 2 for value in query_vector.values()))
    doc_norm = math.sqrt(sum(value ** 2 for value in doc_vector.values()))
    if query_norm == 0 or doc_norm == 0:
        return 0.0
    return dot_product / (query_norm * doc_norm)

def execute_ranked_query(query, vocabulary, inverted_index, folder_path, total_docs, k):
    # Preprocessa la query
    query_terms = preprocess_query(query)
    print(f"Termini della query dopo il preprocessamento: {query_terms}")
    
    # Calcola il vettore TF-IDF della query
    query_tfidf = calculate_query_tfidf(query_terms, vocabulary, inverted_index, total_docs)
    print(f"Vettore TF-IDF della query: {query_tfidf}")
    
    # Calcola la similarità coseno per ciascun documento che contiene almeno un termine della query
    doc_scores = {}
    for term in query_terms:
        if term in inverted_index:
            for doc_id, tfidf_score in inverted_index[term]:
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = defaultdict(float)
                doc_scores[doc_id][term] = tfidf_score
    
    # Calcola la similarità coseno tra la query e ciascun documento
    results = []
    for doc_id, doc_vector in doc_scores.items():
        similarity = cosine_similarity(query_tfidf, doc_vector)
        if similarity > 0:
            results.append((doc_id, similarity))
    
    # Ordina i risultati in base alla similarità e restituisce i top-k
    results = sorted(results, key=lambda x: x[1], reverse=True)[:k]
    
    # Raccolta dei dettagli dei ristoranti per i doc_id trovati
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
    
    # Creazione del DataFrame di risultati per una visualizzazione più pulita
    results_df = pd.DataFrame(restaurant_results, columns=["restaurantName", "address", "description", "website", "similarity_score"])
    return results_df

if __name__ == "__main__":
    # Specifica i file e le cartelle
    vocab_file = "vocabulary.csv"  # Percorso del vocabolario
    index_file = "tfidf_inverted_index.json"  # Percorso dell'indice invertito TF-IDF
    folder_path = "processed_files"  # Cartella dei file preprocessati
    
    # Carica vocabolario e indice invertito
    with open(index_file, 'r') as f:
        inverted_index = json.load(f)
    total_docs = len(os.listdir(folder_path))
    
    # Richiedi la query all'utente
    query = input("Inserisci la tua query: ")
    k = int(input("Inserisci il numero di risultati top-k da visualizzare: "))
    results_df = execute_ranked_query(query, None, inverted_index, folder_path, total_docs, k)
    
    # Mostra i risultati
    if not results_df.empty:
        print(results_df)
    else:
        print("Nessun risultato trovato per la query fornita.")