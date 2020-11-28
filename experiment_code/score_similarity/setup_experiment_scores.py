from cleaned_code.score_similarity.get_foodon_food_context_ppmi import FoodPPMISimScore
from cleaned_code.score_similarity.get_foodon_food_occurrences import FoodCoocSimScore
from cleaned_code.score_similarity.get_foodon_subclass_path import FoodSubclassPaths
from cleaned_code.score_similarity.get_spacy_and_w2v_ing_sims import FoodEmbeddingSims

if __name__ == '__main__':
    food_link_files = ['../data/in/foodon-links-1.ttl']
    foodkg_data_files = ['../data/in/recipes-1.ttl']
    foodon_file = '../data/in/food_on.owl'
    w2v_file = '../data/in/r1m_word2vec/vocab.bin'

    # if something other than the default directories/filenames for outputs of each step are used,
    # they should be set as arguments for the classes.

    print('initial setup')
    FoodSubclassPaths().run(foodon_file=foodon_file, food_link_files=food_link_files)
    print('reformat recipe data, get co-occurrence similarity score')
    FoodCoocSimScore().run(food_link_files=food_link_files, foodkg_data_files=foodkg_data_files)
    print('get PPMI similarity score')
    FoodPPMISimScore().run(food_link_files=food_link_files)
    print('get word2vec and spacy embedding similarity scores')
    FoodEmbeddingSims().run(w2v_file=w2v_file, food_link_files=food_link_files)
