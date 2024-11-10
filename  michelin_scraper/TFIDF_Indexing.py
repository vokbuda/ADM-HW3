import os
import json
import math
from collections import defaultdict
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import csv
import nltk

# Scarica risorse NLTK necessarie
nltk.download('punkt')
nltk.download('stopwords')

# Percorsi dei file e cartelle
DATA_FOLDER = '/Users/fabrizioferrara/Desktop/Progetti DataScience/ADM/michelin_scraper/michelin_restaurant_data'
VOCAB_FILE = 'vocabulary_with_tfidf.csv'  # File vocabolario aggiornato
INDEX_FILE = 'inverted_index_with_tfidf.json'  # File indice invertito aggiornato
DESCRIPTIONS_FILE = '/Users/fabrizioferrara/Desktop/Progetti DataScience/ADM/michelin_scraper/cleaned_descriptions.txt'

# Inizializzazione risorse NLTK
stop_words = set(stopwords.words("english"))
stemmer = PorterStemmer()

# Funzione per preprocessare il testo
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    return [stemmer.stem(word) for word in tokens if word.isalpha() and word not in stop_words]

# Funzione per creare il vocabolario
def create_vocabulary(descriptions):
    vocabulary = {}
    term_id_counter = 0
    for description in descriptions:
        terms = preprocess_text(description)
        for term in terms:
            if term not in vocabulary:
                vocabulary[term] = term_id_counter
                term_id_counter += 1
    return vocabulary

# Funzione per calcolare i punteggi TF-IDF
def compute_tfidf(vocabulary, descriptions):
    term_document_frequency = defaultdict(int)
    term_document_tf = defaultdict(lambda: defaultdict(int))
    
    # Calcola la frequenza dei termini in ciascun documento
    for doc_id, description in enumerate(descriptions, start=1):
        terms = preprocess_text(description)
        for term in terms:
            term_id = vocabulary[term]
            term_document_frequency[term_id] += 1
            term_document_tf[term_id][doc_id] += 1

    # Calcola TF-IDF e crea indice invertito
    inverted_index_with_tfidf = defaultdict(list)
    num_documents = len(descriptions)

    for term_id, doc_freq in term_document_frequency.items():
        idf = math.log(num_documents / doc_freq)
        for doc_id, tf in term_document_tf[term_id].items():
            tf_idf = (tf / len(descriptions[doc_id - 1].split())) * idf
            inverted_index_with_tfidf[term_id].append((doc_id, tf_idf))

    return inverted_index_with_tfidf

# Funzione per salvare il vocabolario in un file CSV
def save_vocabulary(vocabulary, vocab_file):
    with open(vocab_file, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["term", "term_id"])
        for term, term_id in vocabulary.items():
            writer.writerow([term, term_id])
    print(f"\nVocabolario salvato in '{vocab_file}'.")

# Funzione per salvare l'indice invertito con TF-IDF in un file JSON
def save_inverted_index_with_tfidf(inverted_index, index_file):
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, indent=4)
    print(f"Indice invertito con TF-IDF salvato in '{index_file}'.")

# Script principale
if __name__ == "__main__":
    # Carica le descrizioni preprocessate
    with open(DESCRIPTIONS_FILE, 'r', encoding='utf-8') as f:
        descriptions = [line.strip().split("\t")[1] for line in f]

    # Crea il vocabolario e calcola l'indice invertito con TF-IDF
    vocabulary = create_vocabulary(descriptions)
    inverted_index_with_tfidf = compute_tfidf(vocabulary, descriptions)

    # Salva il vocabolario e l'indice invertito con TF-IDF
    save_vocabulary(vocabulary, VOCAB_FILE)
    save_inverted_index_with_tfidf(inverted_index_with_tfidf, INDEX_FILE)
    
    print("\nVocabolario e indice invertito con TF-IDF creati e salvati con successo.")