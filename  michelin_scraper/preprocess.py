import os
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import nltk

# Scarica le risorse necessarie
nltk.download('punkt')
nltk.download('stopwords')

# Funzione per preprocessare il testo
def preprocess_text(text):
    tokens = word_tokenize(text.lower())
    stop_words = set(stopwords.words('english'))
    ps = PorterStemmer()
    cleaned_tokens = [ps.stem(word) for word in tokens if word.isalpha() and word not in stop_words]
    return ' '.join(cleaned_tokens)

# Funzione per preprocessare tutte le descrizioni nei file .tsv
def preprocess_descriptions(input_folder, output_file):
    processed_count = 0
    
    with open(output_file, "w", encoding="utf-8") as outfile:
        for filename in os.listdir(input_folder):
            if filename.endswith(".tsv"):
                with open(os.path.join(input_folder, filename), "r", encoding="utf-8") as infile:
                    lines = infile.readlines()
                    if len(lines) > 1:
                        columns = lines[1].split("\t")
                        if len(columns) > 7:
                            description = columns[7]
                            cleaned_description = preprocess_text(description)
                            outfile.write(f"{filename}\t{cleaned_description}\n")
                            processed_count += 1
                            print(f"Preprocessed: {filename}")
                        else:
                            print(f"Skipping {filename}: Insufficient columns")
                    else:
                        print(f"Skipping {filename}: Empty or incomplete file")
    
    print(f"\nTotal files processed: {processed_count}")

# Specifica il percorso della cartella e del file di output
input_folder = '/Users/fabrizioferrara/Desktop/Progetti DataScience/ADM/michelin_scraper/michelin_restaurant_data'
output_file = '/Users/fabrizioferrara/Desktop/Progetti DataScience/ADM/michelin_scraper/cleaned_descriptions.txt'

# Esegui la funzione di preprocessamento
preprocess_descriptions(input_folder, output_file)