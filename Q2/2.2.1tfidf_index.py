import os
import pandas as pd
import json
import math
from collections import defaultdict, Counter

def calculate_tf_idf(folder_path, output_index_file):
    #dictionaries for TF and count of documents containing each term
    term_doc_freq = defaultdict(int)  #document count for each term
    doc_term_freq = {}  
    total_docs = 0  
    total_terms = 0  
    unique_terms = set()  #set to track unique terms

    #calculating frequencies
    print("Start processing documents...")
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsv"):
            file_path = os.path.join(folder_path, filename)
            doc_id = filename.split('.')[0]
            
            df = pd.read_csv(file_path, sep='\t')
            if 'processed_description' in df.columns:
                description = df['processed_description'].iloc[0]
                
                #tokenize the description and count the frequency of the terms
                terms = description.split()
                total_terms += len(terms)  #add the number of terms
                term_freq = Counter(terms)
                doc_term_freq[doc_id] = term_freq  #save TF for this document
                total_docs += 1  
                
                #increase the document count for each term and add unique terms
                for term in term_freq.keys():
                    term_doc_freq[term] += 1
                    unique_terms.add(term)

    print(f"Total documents processed: {total_docs}")
    print(f"Total words processed: {total_terms}")
    print(f"Total number of unique terms in the vocabulary: {len(unique_terms)}")

    #calculate TF-IDF and construct the inverted index
    print("Calculating TF-IDF scores and constructing the inverted index...")
    tfidf_index = defaultdict(list)
    for doc_id, term_freq in doc_term_freq.items():
        norm_factor = math.sqrt(sum((tf / sum(term_freq.values())) ** 2 for tf in term_freq.values()))  #normalization
        for term, tf in term_freq.items():
            #calculate TF (term frequency / total terms in document)
            tf_value = tf / sum(term_freq.values())
            #calculate IDF (logarithm of total number of documents divided by documents containing the term)
            idf_value = math.log(total_docs / (1 + term_doc_freq[term]))
            #calculate TF-IDF
            tfidf_score = tf_value * idf_value
            #normalize TF-IDF
            tfidf_score /= norm_factor if norm_factor > 0 else 1
            
            tfidf_index[term].append((doc_id, tfidf_score))

    print("Inverted index with TF-IDF successfully constructed")

    #saves inverted index with TF-IDF
    with open(output_index_file, 'w') as f:
        json.dump(tfidf_index, f, indent=4)
    
    print(f"Inverted index with TF-IDF saved in {output_index_file}")

if __name__ == "__main__":
    folder_path = "processed_files"  
    output_index_file = "tfidf_inverted_index.json"  #output file
    
    calculate_tf_idf(folder_path, output_index_file)