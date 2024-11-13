import os
import pandas as pd
import json
import re
import math
import heapq
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

def load_index(vocab_file, index_file):
    # Carica il vocabolario e l'indice invertito TF-IDF
    vocab_df = pd.read_csv(vocab_file)
    vocabulary = dict(zip(vocab_df['term'], vocab_df['term_id']))
    
    with open(index_file, 'r') as f:
        inverted_index = json.load(f)
        
    return vocabulary, inverted_index

def custom_score(restaurant, query_terms, tfidf_scores):
    # Pesi massimi normalizzati per ciascun fattore
    description_weight = 0.45
    cuisine_weight = 0.30
    facilities_weight = 0.05
    price_weight = 0.20

    score = 0

    # Punteggio per il match nella descrizione basato su TF-IDF
    description_tfidf_score = sum(tfidf_scores.get(term, 0) for term in query_terms)
    max_tfidf_score = sum(tfidf_scores.get(term, 0) for term in query_terms if term in tfidf_scores)
    if max_tfidf_score > 0:
        score += (description_tfidf_score / max_tfidf_score) * description_weight

    # Punteggio per il tipo di cucina
    cuisine_types = str(restaurant.get('cuisineType', '')).lower().split(',')
    cuisine_matches = sum(1 for term in query_terms if term in cuisine_types)
    if cuisine_matches > 0:
        score += (cuisine_matches / len(query_terms)) * cuisine_weight

    # Punteggio per i servizi e le facilities
    facilities = str(restaurant.get('facilitiesServices', '')).lower()
    facilities_matches = sum(1 for term in query_terms if term in facilities)
    if facilities_matches > 0:
        score += (facilities_matches / len(query_terms)) * facilities_weight

    # Punteggio per la fascia di prezzo
    price = restaurant.get('priceRange', '')
    if price == '€':
        score += price_weight  # punteggio massimo per fascia economica
    elif price == '€€':
        score += price_weight * 0.75
    elif price == '€€€':
        score += price_weight * 0.5
    elif price == '€€€€':
        score += price_weight * 0.25

    return round(score, 2)

def execute_custom_ranked_query(query, vocabulary, inverted_index, folder_path, k):
    # Preprocessa la query
    query_terms = preprocess_query(query)
    print(f"Termini della query dopo il preprocessamento: {query_terms}")
    
    # Recupera i documenti rilevanti utilizzando l'indice invertito TF-IDF
    tfidf_scores = defaultdict(lambda: defaultdict(float))
    for term in query_terms:
        term_id = vocabulary.get(term)
        if term_id and str(term_id) in inverted_index:
            for doc_id, tfidf_score in inverted_index[str(term_id)]:
                tfidf_scores[doc_id][term] = tfidf_score

    # Calcola i punteggi personalizzati per ciascun documento
    results = []
    for doc_id, doc_tfidf in tfidf_scores.items():
        # Carica i dettagli del ristorante
        file_path = os.path.join(folder_path, f"{doc_id}.tsv")
        df = pd.read_csv(file_path, sep='\t')
        restaurant = df.iloc[0].to_dict()
        
        # Calcola il punteggio personalizzato
        score = custom_score(restaurant, query_terms, doc_tfidf)
        # Usa -score per il max-heap e aggiungi doc_id come secondo elemento
        heapq.heappush(results, (-score, doc_id, restaurant))

        # Mantieni solo i top-k risultati
        if len(results) > k:
            heapq.heappop(results)
    
    # Ordina e formatta i risultati
    top_results = sorted(results, key=lambda x: -x[0])
    output = [{
        "restaurantName": doc['restaurantName'],
        "address": doc['address'],
        "description": doc['description'],
        "website": doc['website'],
        "custom_score": -score
    } for score, _, doc in top_results]
    
    # Creazione del DataFrame di risultati per una visualizzazione più pulita
    results_df = pd.DataFrame(output, columns=["restaurantName", "address", "description", "website", "custom_score"])
    return results_df

if __name__ == "__main__":
    # Specifica i file e le cartelle
    vocab_file = "vocabulary.csv"  # Percorso del vocabolario
    index_file = "tfidf_inverted_index.json"  # Percorso dell'indice invertito TF-IDF
    folder_path = "processed_files"  # Cartella dei file preprocessati
    
    # Carica vocabolario e indice invertito
    vocabulary, inverted_index = load_index(vocab_file, index_file)
    
    # Richiedi la query all'utente
    query = input("Inserisci la tua query: ")
    k = int(input("Inserisci il numero di risultati top-k da visualizzare: "))
    results_df = execute_custom_ranked_query(query, vocabulary, inverted_index, folder_path, k)
    
    # Mostra i risultati
    if not results_df.empty:
        print(results_df)
    else:
        print("Nessun risultato trovato per la query fornita.")