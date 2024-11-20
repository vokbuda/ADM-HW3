import os
import pandas as pd
import nltk
import re
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer

nltk.download('stopwords')

#to remove common words from texts (stopwords) and reduce words to their root (stemming)
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

#text processing
def preprocess_text(text):
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    tokens = [stemmer.stem(word) for word in text.split() if word not in stop_words]
    return ' '.join(tokens)
#Process restaurant descriptions in TSV files
def preprocess_restaurant_descriptions(folder_path, output_folder):
    os.makedirs(output_folder, exist_ok=True)
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsv"):
            file_path = os.path.join(folder_path, filename)
            
            df = pd.read_csv(file_path, sep='\t')
            #create a new column 'processed_description'
            df['processed_description'] = df['description'].apply(preprocess_text)
            
            output_path = os.path.join(output_folder, filename)
            df.to_csv(output_path, sep='\t', index=False)

if __name__ == "__main__":
    
    folder_path = "restaurants_tsv"  #folder with input files
    output_folder = "processed_files"  #folder with output files
    
    preprocess_restaurant_descriptions(folder_path, output_folder)