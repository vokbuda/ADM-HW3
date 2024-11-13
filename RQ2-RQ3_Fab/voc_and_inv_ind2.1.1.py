import os
import pandas as pd
import json
from collections import defaultdict
def build_vocabulary_and_inverted_index(folder_path, output_vocab_file, output_index_file):
    vocabulary = {}
    inverted_index = defaultdict(list)
    term_id_counter = 0
    files_processed = 0  # Contatore per i file processati
    skipped_files = []  # Lista per tracciare i file con descrizioni non valide
    
    # Scorri attraverso ogni file TSV nella cartella
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsv"):
            file_path = os.path.join(folder_path, filename)
            doc_id = filename.split('.')[0]  # Usiamo il nome del file come doc_id
            
            # Carica il file TSV
            df = pd.read_csv(file_path, sep='\t')
            
            # Verifica che la colonna 'processed_description' esista
            if 'processed_description' in df.columns:
                # Ottieni la descrizione preprocessata e verifica che sia una stringa
                description = df['processed_description'].iloc[0]
                if not isinstance(description, str):
                    print(f"Descrizione non valida nel file {filename}, saltato.")
                    skipped_files.append(filename)  # Aggiungi il file alla lista dei saltati
                    continue  # Salta questo documento se la descrizione non è valida
                
                # Tokenizza la descrizione
                terms = description.split()
                print(f"Token nella descrizione di {filename}: {terms}")  # Verifica i termini estratti
                
                # Aggiorna il vocabolario e l'indice invertito
                for term in terms:
                    if term not in vocabulary:
                        # Assegna un nuovo term_id se il termine è nuovo
                        vocabulary[term] = term_id_counter
                        term_id_counter += 1
                        print(f"Nuovo termine aggiunto al vocabolario: {term} -> term_id {vocabulary[term]}")
                    
                    term_id = vocabulary[term]
                    
                    # Aggiungi il documento corrente alla lista per il term_id, se non è già presente
                    if doc_id not in inverted_index[term_id]:
                        inverted_index[term_id].append(doc_id)
                        print(f"Aggiunto doc_id {doc_id} per term_id {term_id}")
            
            files_processed += 1  # Incrementa il contatore dei file processati
    
    # Salva il vocabolario su CSV
    vocab_df = pd.DataFrame(list(vocabulary.items()), columns=['term', 'term_id'])
    vocab_df.to_csv(output_vocab_file, index=False)
    print(f"Vocabolario salvato in {output_vocab_file}")
    
    # Salva l'indice invertito su file JSON
    with open(output_index_file, 'w') as f:
        json.dump(inverted_index, f, indent=4)
    print(f"Indice invertito salvato in {output_index_file}")
    
    # Stampa i conteggi finali
    print(f"Numero totale di file processati: {files_processed}")
    print(f"Numero totale di termini unici nel vocabolario: {len(vocabulary)}")
    
    # Stampa i file saltati
    if skipped_files:
        print("File con descrizioni non valide (non processati):")
        for filename in skipped_files:
            print(f"- {filename}")

if __name__ == "__main__":
    folder_path = "processed_files"  
    output_vocab_file = "vocabulary.csv"  
    output_index_file = "inverted_index.json" 
    
    build_vocabulary_and_inverted_index(folder_path, output_vocab_file, output_index_file)