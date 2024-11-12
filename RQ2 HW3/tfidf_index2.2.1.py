import os
import pandas as pd
import json
import math
from collections import defaultdict, Counter

def calculate_tf_idf(folder_path, output_index_file):
    # Dizionari per TF e conteggio dei documenti contenenti ciascun termine
    term_doc_freq = defaultdict(int)  # Conteggio di documenti per ogni termine
    doc_term_freq = {}  # TF per ogni termine in ogni documento
    total_docs = 0  # Conteggio dei documenti

    # Fase 1: Calcola TF e conta i documenti per ogni termine
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsv"):
            file_path = os.path.join(folder_path, filename)
            doc_id = filename.split('.')[0]
            
            df = pd.read_csv(file_path, sep='\t')
            if 'processed_description' in df.columns:
                description = df['processed_description'].iloc[0]
                
                # Tokenizza la descrizione e conta la frequenza dei termini
                terms = description.split()
                term_freq = Counter(terms)
                doc_term_freq[doc_id] = term_freq  # Salva TF per questo documento
                total_docs += 1  # Incrementa il conteggio dei documenti
                
                # Incrementa il conteggio dei documenti per ciascun termine
                for term in term_freq.keys():
                    term_doc_freq[term] += 1

    # Fase 2: Calcola TF-IDF e costruisce l'indice invertito
    tfidf_index = defaultdict(list)
    for doc_id, term_freq in doc_term_freq.items():
        for term, tf in term_freq.items():
            # Calcola TF (frequenza del termine / totale termini nel documento)
            tf_value = tf / sum(term_freq.values())
            # Calcola IDF (logaritmo del numero totale di documenti diviso i documenti che contengono il termine)
            idf_value = math.log(total_docs / (1 + term_doc_freq[term]))
            # Calcola TF-IDF
            tfidf_score = tf_value * idf_value
            
            # Ottieni o assegna un term_id (opzionale, potresti usare il termine come chiave direttamente)
            tfidf_index[term].append((doc_id, tfidf_score))

    # Salva l'indice invertito con TF-IDF su file JSON
    with open(output_index_file, 'w') as f:
        json.dump(tfidf_index, f, indent=4)
    
    print(f"Indice invertito con TF-IDF salvato in {output_index_file}")

if __name__ == "__main__":
    folder_path = "processed_files"  # Cartella dei file preprocessati
    output_index_file = "tfidf_inverted_index.json"  # File di output per l'indice invertito TF-IDF
    
    calculate_tf_idf(folder_path, output_index_file)