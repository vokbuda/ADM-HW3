import os
import json
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from collections import defaultdict
import csv

# Percorsi dei file e cartelle
DATA_FOLDER = 'restaurants_tsv'
VOCAB_FILE = 'vocabulary.csv'  
INDEX_FILE = 'inverted_index.json'  
DESCRIPTIONS_FILE = 'cleaned_descriptions.txt'

# Funzione per preprocessare i termini
def preprocess_text(text):
    stop_words = set(stopwords.words("english"))
    stemmer = PorterStemmer()
    tokens = word_tokenize(text.lower())
    return [stemmer.stem(word) for word in tokens if word.isalpha() and word not in stop_words]

# Funzione per creare vocabolario e indice invertito
def create_vocabulary_and_index(descriptions_file):
    vocabulary = {}
    inverted_index = defaultdict(list)
    term_id_counter = 0

    with open(descriptions_file, 'r', encoding='utf-8') as file:
        for doc_id, line in enumerate(file, start=1):
            filename, cleaned_description = line.strip().split("\t")
            terms = preprocess_text(cleaned_description)
            for term in terms:
                if term not in vocabulary:
                    vocabulary[term] = term_id_counter
                    term_id_counter += 1
                term_id = vocabulary[term]
                
                if doc_id not in inverted_index[term_id]:
                    #if filename == "restaurant_1544.tsv" and term=='modern':  # Salta le righe vuote
                    num_file=filename.replace('.tsv','').split('_')[1]
                    inverted_index[term_id].append(num_file)

    print(f"\nTotale termini unici nel vocabolario: {len(vocabulary)}")
    print(f"Totale documenti processati: {doc_id}")
    return vocabulary, inverted_index

# Funzione per salvare il vocabolario in un file CSV
def save_vocabulary(vocabulary, vocab_file):
    with open(vocab_file, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["term", "term_id"])
        for term, term_id in vocabulary.items():
            writer.writerow([term, term_id])
    print(f"\nVocabolario salvato in '{vocab_file}'.")

# Funzione per salvare l'indice invertito in un file JSON
def save_inverted_index(inverted_index, index_file):
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(inverted_index, f, indent=4)
    print(f"Indice invertito salvato in '{index_file}'.")

if __name__ == "__main__":
    vocabulary, inverted_index = create_vocabulary_and_index(DESCRIPTIONS_FILE)
    save_vocabulary(vocabulary, VOCAB_FILE)
    save_inverted_index(inverted_index, INDEX_FILE)
    
    print("\nVocabolario e indice invertito creati e salvati con successo.")