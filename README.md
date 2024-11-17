# ADM-HW3 Homework 3 - Michelin restaurants in Italy
This repository contains the solution of the third homework of the Algorithmic Methods of Data Mining course.
We answered research questions (RQs) about [Michelin restaurants](https://guide.michelin.com/en/it/restaurants) dataset, in order to preprocess data and make some analysis related to these restaurants.



The repository consists of the following folders/files:
1. __`RQ1`__:
    > `get_ursl.py` is a file which gets all urls and saves it into file `.txt`.<br>
    > `get_html.py` saves source code into related `.html` file<br>
    > `extract_info.py` is a file which gets information related to each restaurant and saves it into tsv files
2. __`RQ2`__:
    - `2.0.0preprocessing.py` is a file that processes the `.tsv` files generated in RQ1. It adds a new column containing cleaned and preprocessed descriptions. The output is             saved in the `processed_files` folder, with one processed file per restaurant.
    - `2.1.1voc_and_inv_ind.py` is a file that builds a vocabulary and an inverted index from TSV files containing preprocessed Michelin restaurant descriptions. The output files         are `vocabulary.csv` and `inverted_index.json`.
    - `2.1.2execute_query.py` is a file that runs a conjunctive query on the preprocessed restaurant data, using a previously generated vocabulary and inverted index.
    - `2.2.1tfidf_index.py` is a file that calculates Term Frequency-Inverse Document Frequency (TF-IDF) scores for terms in preprocessed restaurant descriptions and builds an             inverted index based on those scores. The output file is `tfidf_inverted_index.json`.
    - `2.2.2ranked_query.py` is a file that implements a ranked search engine for Michelin restaurants, based on TF-IDF scores and cosine similarity between the query and                 preprocessed documents.
2. __`RQ3`__:  
    - `3custom_score.py` is a file that implements a custom-ranked search engine for Michelin restaurants. It combines TF-IDF scores with a personalized ranking score based on             additional factors, such as cuisine type, price range, and services.

     **Research Questions:**
    1. **[RQ1]**: Data collection (crawl, scraper, parser)  
    2. **[RQ2]**: Preprocessing, conjunctive query, index creation, ranked search
    3. **[RQ3]**: Define a new score  
    4. **[RQ4]**: Visualizing the most important restaurant(plotting)

    **Bonus Question**:  
    > 

    **Algorithmic Question (AQ)**
    > `AQ.ipynb` is a file where we solve AQ question
4. __`LICENSE`__: 
> This project is licensed under the [MIT License](./LICENSE).
