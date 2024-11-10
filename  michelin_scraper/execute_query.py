import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import nltk
from collections import defaultdict

# Scarica le risorse necessarie


# Percorsi dei file e cartelle
DATA_FOLDER = 'michelin_restaurant_data'
VOCAB_FILE = 'vocabulary.csv'  
INDEX_FILE = 'inverted_index.json'  

# Funzione per caricare il vocabolario
def load_vocabulary(file_path):
    vocabulary = {}
    with open(file_path, mode='r', encoding='utf-8') as f:
        next(f)  # Salta l'intestazione
        for line in f:
            term, term_id = line.strip().split(',')
            vocabulary[term] = int(term_id)
    return vocabulary

# Funzione per caricare l'indice invertito
def load_inverted_index(file_path):
    import json
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# Funzione per preprocessare la query
def preprocess_query(query):
    stop_words = set(stopwords.words("english"))
    stemmer = PorterStemmer()
    tokens = word_tokenize(query.lower())
    return [stemmer.stem(token) for token in tokens if token.isalpha() and token not in stop_words]

# Funzione per eseguire la query
def execute_query(query, vocabulary, inverted_index):
    query_terms = preprocess_query(query)
    print(f"Termini preprocessati della query: {query_terms}")
    
    # Trova i documenti che contengono tutti i termini della query
    doc_sets = []
    for term in query_terms:
        if term in vocabulary:
            term_id = vocabulary[term]
            print(f"Termine '{term}' trovato con term_id {term_id}")
            doc_sets.append(set(inverted_index.get(str(term_id), [])))
        else:
            print(f"Termine '{term}' non trovato nel vocabolario.")
            return []

    # Intersezione per ottenere documenti che contengono tutti i termini della query
    if not doc_sets:
        return []
    matching_docs = set.intersection(*doc_sets)
    print(f"Documenti che contengono tutti i termini della query: {matching_docs}")
    
    # Estrai i dettagli dei ristoranti dai file .tsv
    results = []
    for doc_id in matching_docs:
        tsv_file = os.path.join(DATA_FOLDER, f"restaurant_{doc_id}.tsv")
        if os.path.isfile(tsv_file):
            with open(tsv_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                if len(lines) > 1:
                    columns = lines[1].split("\t")
                    if len(columns) > 11:  # Verifica che ci siano abbastanza colonne
                        restaurant_info = {
                            "restaurantName": columns[0],
                            "address": columns[1],
                            "description": columns[7],
                            "website": columns[11].strip()  # Colonna corretta per l'URL del sito
                        }
                        results.append(restaurant_info)
                        print(f" - Trovato ristorante: {restaurant_info}")
        else:
            print(f"File non trovato per il documento {doc_id}")
    
    return results

# Funzione principale
if __name__ == "__main__":
    # Carica vocabolario e indice invertito
    nltk.download('punkt')
    nltk.download('wordnet')
    nltk.download('omw-1.4')
    vocabulary = load_vocabulary(VOCAB_FILE)
    inverted_index = load_inverted_index(INDEX_FILE)
    
    # Esegui la query
    query = input("Inserisci la tua query: ")
    results = execute_query(query, vocabulary, inverted_index)
    
    # Stampa i risultati
    if results:
        print("\nRistoranti trovati per la query '{}':\n".format(query))
        for result in results:
            print(f"Restaurant Name: {result['restaurantName']}")
            print(f"Address: {result['address']}")
            print(f"Description: {result['description'][:100]}...")  # Mostra solo i primi 100 caratteri
            print(f"Website: {result['website']}\n")
    else:
        print("Nessun ristorante trovato per questa query.")