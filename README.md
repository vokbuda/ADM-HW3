# ADM-HW3 Homework 3 - Michelin restaurants in Italy
This repository contains the solution of the third homework of the Algorithmic Methods of Data Mining course.
We answered research questions (RQs) about [Michelin restaurants](https://guide.michelin.com/en/it/restaurants) dataset, in order to preprocess data and make some analysis related to these restaurants.



The repository consists of the following folders/files:
1. __`RQ1`__:
    > `get_ursl.py` is a file which gets all urls and saves it into file `.txt`.<br>
    > `get_html.py` saves source code into related `.html` file<br>
    > `extract_info.py` is a file which gets information related to each restaurant and saves it into tsv files
2. __`RQ2`__:
    - `2.0.0preprocessing.py` is a file that processes the `.tsv` files generated in RQ1. It adds a new column with cleaned and preprocessed descriptions. The output is saved in         the folder `processed_files`, containing one processed file per restaurant.
     


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
