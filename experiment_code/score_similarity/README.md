Run the setup_experiment_scores script to compute scores for ingredient substitutability using a few different methods.

Running the script requires you to collect several pieces of data and place them into the data/in directory.

### FOODKG data

Find the most up-to-date instructions to construct the FoodKG [here](https://foodkg.github.io/foodkg.html).

After running the code to generate the FoodKG, you should have some files containing recipe data (like 'foodkg-core.trig') 
and containing links from FoodKG ingredient URIs to FoodOn class URIs (like 'foodon-links.trig'). Depending on how much
of the data you use to construct the FoodKG, you may have multiple files of recipe data.

Once you have constructed the FoodKG, move these files into the data/in directory. In the setup_experiment_scores script,
point the foodkg_data_files variable to your recipe data and food_link_files to your foodon-links file.

### FoodOn

Download the FoodOn ontology, e.g. by using [OntoFox](http://ontofox.hegroup.org/). If using OntoFox, set the low level 
source term URI as
```
http://purl.obolibrary.org/obo/FOODON_00001002 
includeAllChildren
```

and include the rdfs:subClassOf annotations.

Move the downloaded FoodOn ontology to data/in, and make sure the foodon_file variable in the setup_experiment_scores
script is pointing to the right file.

### Word2Vec model

Data for a Word2Vec model trained on data from [Recipe1M+](http://pic2recipe.csail.mit.edu/) can be downloaded from
[here](http://im2recipe.csail.mit.edu/dataset/login/). (this should be the same place where you had to get data in 
order to construct the FoodKG). 

Download vocab.bin.gz from the Model training files. Extract the vocab file, and move it
to somewhere appropriate in the data/in directory. Make sure the w2v_file variable in the setup_experiment_scores
script is pointing to the right file.

### spaCy

The current code uses the en_core_web_lg model from spaCy. You may need to download this manually 
(details [here](https://spacy.io/models/en)). 

## Run the code

Once the data files are in the appropriate locations you should be able to run the setup_experiment_scores script.
