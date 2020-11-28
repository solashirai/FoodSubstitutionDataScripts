from cleaned_code.score_similarity.get_foodon_food_context_ppmi import FoodPPMISimScore
from cleaned_code.score_similarity.get_foodon_food_occurrences import FoodCoocSimScore
from cleaned_code.score_similarity.get_foodon_subclass_path import FoodSubclassPaths
from cleaned_code.score_similarity.get_spacy_and_w2v_ing_sims import FoodEmbeddingSims

if __name__ == '__main__':
    print('initial setup')
    FoodSubclassPaths().run()
    print('reformat recipe data, get co-occurrence similarity score')
    FoodCoocSimScore().run()
    print('get PPMI similarity score')
    FoodPPMISimScore().run()
    print('get word2vec and spacy embedding similarity scores')
    FoodEmbeddingSims().run()