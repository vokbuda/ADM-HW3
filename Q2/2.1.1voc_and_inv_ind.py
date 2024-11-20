import os
import pandas as pd
import json
from collections import defaultdict
def build_vocabulary_and_inverted_index(folder_path, output_vocab_file, output_index_file):
    vocabulary = {}
    inverted_index = defaultdict(list)
    term_id_counter = 0  #counter to assign term_ids
    files_processed = 0  #counter for processed files
    skipped_files = []  #list for skipped files
    
    for filename in os.listdir(folder_path):
        if filename.endswith(".tsv"):
            file_path = os.path.join(folder_path, filename)
            doc_id = filename.split('.')[0]  #use the file name (without extension) as 'doc_id'
            
            df = pd.read_csv(file_path, sep='\t')
            
            #verify that the 'processed_description' column exists
            if 'processed_description' in df.columns:
                description = df['processed_description'].iloc[0]
                if not isinstance(description, str):
                    print(f"Invalid description in file {filename}, skipped.")
                    skipped_files.append(filename)  #record skipped files
                    continue  
                #tokenize the description
                terms = description.split()
                print(f"Token in the description of {filename}: {terms}")  
                
                #update the vocabulary and the inverted index
                for term in terms:
                    if term not in vocabulary:
                        
                        vocabulary[term] = term_id_counter
                        term_id_counter += 1
                        print(f"New term added to the vocabulary: {term} -> term_id {vocabulary[term]}")
                    
                    term_id = vocabulary[term]
                    
                    #adds the current document to the list for the term_id, if it is not already present
                    if doc_id not in inverted_index[term_id]:
                        inverted_index[term_id].append(doc_id)
                        print(f"Added doc_id {doc_id} for term_id {term_id}")
            
            files_processed += 1  
    
    #saves the vocabulary
    vocab_df = pd.DataFrame(list(vocabulary.items()), columns=['term', 'term_id'])
    vocab_df.to_csv(output_vocab_file, index=False)
    print(f"Vocabulary saved in {output_vocab_file}")
    
    #saves the inverted index
    with open(output_index_file, 'w') as f:
        json.dump(inverted_index, f, indent=4)
    print(f"Inverted index saved in {output_index_file}")
    
    #print final counts
    print(f"Total number of files processed: {files_processed}")
    print(f"Total number of unique terms in the vocabulary: {len(vocabulary)}")
    
    #print the skipped files
    if skipped_files:
        print("Files with invalid descriptions (not processed):")
        for filename in skipped_files:
            print(f"- {filename}")

if __name__ == "__main__":
    folder_path = "processed_files"  #folder with input files
    output_vocab_file = "vocabulary.csv"  #A CSV file that assigns a unique term_id to each term found in the preprocessed descriptions
    output_index_file = "inverted_index.json" #A JSON file that maps each term_id to a list of doc_ids (documents) in which the term appears
    
    build_vocabulary_and_inverted_index(folder_path, output_vocab_file, output_index_file)