import os
import pandas as pd
import json
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

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
    # Carica il vocabolario e l'indice invertito
    vocab_df = pd.read_csv(vocab_file)
    vocabulary = dict(zip(vocab_df['term'], vocab_df['term_id']))
    
    with open(index_file, 'r') as f:
        inverted_index = json.load(f)
        
    return vocabulary, inverted_index

def execute_conjunctive_query(query, vocabulary, inverted_index, folder_path):
    # Preprocessa la query
    query_terms = preprocess_query(query)
    print(f"Termini della query dopo il preprocessamento: {query_terms}")
    
    # Trova i term_id per ogni termine della query
    term_ids = [vocabulary.get(term) for term in query_terms if term in vocabulary]
    term_ids = [term_id for term_id in term_ids if term_id is not None]
    print(f"term_id trovati nella query: {term_ids}")
    
    if not term_ids:
        print("Nessun termine della query trovato nel vocabolario.")
        return []

    # Trova i doc_id che contengono tutti i term_id (operazione congiuntiva)
    doc_sets = [set(inverted_index[str(term_id)]) for term_id in term_ids if str(term_id) in inverted_index]
    common_docs = set.intersection(*doc_sets) if doc_sets else set()
    print(f"doc_id comuni trovati: {common_docs}")
    
    # Raccolta dei dettagli dei ristoranti per i doc_id trovati
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
    
    # Creazione del DataFrame di risultati per una visualizzazione più pulita
    results_df = pd.DataFrame(results, columns=["restaurantName", "address", "description", "website"])
    return results_df

if __name__ == "__main__":
    # Specifica i file e le cartelle
    vocab_file = "vocabulary.csv"  # Percorso del vocabolario
    index_file = "inverted_index.json"  # Percorso dell'indice invertito
    folder_path = "processed_files"  # Cartella dei file preprocessati
    
    # Carica vocabolario e indice invertito
    vocabulary, inverted_index = load_index(vocab_file, index_file)
    
    # Richiedi la query all'utente
    query = input("Inserisci la tua query: ")
    results_df = execute_conjunctive_query(query, vocabulary, inverted_index, folder_path)
    
    # Mostra i risultati
    if not results_df.empty:
        print(results_df)
    else:
        print("Nessun risultato trovato per la query fornita.")