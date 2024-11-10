import os
import json
import math
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import nltk

# Scarica le risorse necessarie
nltk.download('punkt')
nltk.download('stopwords')

# Percorsi dei file e cartelle
DATA_FOLDER = '/Users/fabrizioferrara/Desktop/Progetti DataScience/ADM/michelin_scraper/michelin_restaurant_data'
VOCAB_FILE = 'vocabulary_with_tfidf.csv'
INDEX_FILE = 'inverted_index_with_tfidf.json'

# Funzione per caricare il vocabolario
def load_vocabulary(file_path):
    vocabulary = {}
    with open(file_path, mode='r', encoding='utf-8') as f:
        next(f)  # Salta l'intestazione
        for line in f:
            term, term_id = line.strip().split(',')
            vocabulary[term] = int(term_id)
    return vocabulary

# Funzione per caricare l'indice invertito con TF-IDF
def load_inverted_index(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Funzione per preprocessare la query
def preprocess_query(query):
    stop_words = set(stopwords.words("english"))
    stemmer = PorterStemmer()
    tokens = word_tokenize(query.lower())
    return [stemmer.stem(token) for token in tokens if token.isalpha() and token not in stop_words]

# Funzione per calcolare la similarità coseno
def cosine_similarity(query_vector, doc_vector):
    dot_product = sum(query_vector[term] * doc_vector.get(term, 0) for term in query_vector)
    query_norm = math.sqrt(sum(val ** 2 for val in query_vector.values()))
    doc_norm = math.sqrt(sum(val ** 2 for val in doc_vector.values()))
    if query_norm * doc_norm == 0:
        return 0
    return dot_product / (query_norm * doc_norm)

# Funzione per eseguire la query con similarità coseno
def execute_ranked_query(query, vocabulary, inverted_index, top_k):
    query_terms = preprocess_query(query)
    query_vector = {}

    # Calcola il vettore TF-IDF della query
    for term in query_terms:
        if term in vocabulary:
            term_id = vocabulary[term]
            df = len(inverted_index.get(str(term_id), []))
            idf = math.log((1 + len(inverted_index)) / (1 + df))  # Calcola IDF
            query_vector[term_id] = idf  # Supponiamo tf=1 per ogni termine della query

    # Calcola la similarità coseno per i documenti che contengono termini della query
    doc_scores = {}
    for term_id, query_weight in query_vector.items():
        if str(term_id) in inverted_index:
            for doc_id, tf_idf in inverted_index[str(term_id)]:
                if doc_id not in doc_scores:
                    doc_scores[doc_id] = {}
                doc_scores[doc_id][term_id] = tf_idf

    # Calcola la similarità coseno per ogni documento
    ranked_results = []
    for doc_id, doc_vector in doc_scores.items():
        score = cosine_similarity(query_vector, doc_vector)
        if score > 0:
            ranked_results.append((doc_id, score))

    # Ordina i risultati in base al punteggio di similarità e mostra i top-k risultati
    ranked_results = sorted(ranked_results, key=lambda x: x[1], reverse=True)[:top_k]
    
    # Mostra i risultati
    results = []
    for doc_id, score in ranked_results:
        tsv_file = os.path.join(DATA_FOLDER, f"restaurant_{doc_id}.tsv")
        if os.path.isfile(tsv_file):
            with open(tsv_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > 1:
                    columns = lines[1].split("\t")
                    if len(columns) > 11:
                        restaurant_info = {
                            "restaurantName": columns[0],
                            "address": columns[1],
                            "description": columns[7],
                            "website": columns[11].strip(),
                            "similarity_score": round(score, 4)
                        }
                        results.append(restaurant_info)

    return results

# Funzione principale
if __name__ == "__main__":
    # Carica vocabolario e indice invertito
    vocabulary = load_vocabulary(VOCAB_FILE)
    inverted_index = load_inverted_index(INDEX_FILE)
    
    # Esegui la query
    query = input("Inserisci la tua query: ")
    top_k = int(input("Inserisci il numero di risultati top-k da visualizzare: "))
    results = execute_ranked_query(query, vocabulary, inverted_index, top_k=top_k)
    
    # Stampa i risultati
    if results:
        print("\nRistoranti trovati per la query '{}':\n".format(query))
        for result in results:
            print(f"Restaurant Name: {result['restaurantName']}")
            print(f"Address: {result['address']}")
            print(f"Description: {result['description'][:100]}...")  # Mostra solo i primi 100 caratteri
            print(f"Website: {result['website']}")
            print(f"Similarity Score: {result['similarity_score']}\n")
    else:
        print("Nessun ristorante trovato per questa query.")