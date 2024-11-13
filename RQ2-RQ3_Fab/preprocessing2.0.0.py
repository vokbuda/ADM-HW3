import os
import pandas as pd
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

# Assicuriamoci che le risorse di nltk siano disponibili
nltk.download('stopwords')

# Definisci la lista delle stopword e lo stemmer
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess_text(text):
    # Verifica che il testo sia una stringa, altrimenti restituisce una stringa vuota
    if not isinstance(text, str):
        return ""
    # Converti il testo in minuscolo
    text = text.lower()
    # Rimuovi la punteggiatura
    text = re.sub(r'[^\w\s]', '', text)
    # Tokenizza, rimuovi le stopword e applica lo stemming
    tokens = [stemmer.stem(word) for word in text.split() if word not in stop_words]
    return ' '.join(tokens)

def preprocess_restaurant_descriptions(folder_path, output_folder):
    # Assicura che la cartella di output esista
    os.makedirs(output_folder, exist_ok=True)
    
    # Scorri attraverso ogni file TSV nella cartella
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsv"):
            file_path = os.path.join(folder_path, filename)
            
            # Leggi il file TSV con nomi di colonna
            df = pd.read_csv(file_path, sep='\t')
            
            # Applica il preprocessamento alla colonna description
            df['processed_description'] = df['description'].apply(preprocess_text)
            
            # Salva il dataframe preprocessato
            output_path = os.path.join(output_folder, filename)
            df.to_csv(output_path, sep='\t', index=False)

if __name__ == "__main__":
    
    folder_path = "restaurants_tsv"  
    output_folder = "processed_files"  
    
    preprocess_restaurant_descriptions(folder_path, output_folder)