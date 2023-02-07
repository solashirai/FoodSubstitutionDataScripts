import rdflib
import pickle
from collections import defaultdict
import numpy as np
import json
import time
from scipy.sparse import csr_matrix, lil_matrix
from experiment_code.score_similarity.rec_to_vec import RecToVec


class FoodCoocSimScore:

    def run(self,*,
            foodon_to_root_file = '../data/out/foodon_to_root_path.pkl',
            index_dict_file = '../data/out/food_index_dict.pkl',
            foodkg_data_files = ['../data/in/recipes-1.ttl'],
            food_link_files = ['../data/in/foodon-links-1.ttl'],
            save_coocurrence_matrix = '../data/out/food_coocurrence_mat.pkl',
            save_ocurrence_dict = '../data/out/food_ocurrence_dict.pkl',
            save_cooc_sim_dict = '../data/out/food_cooc_sim_dict.pkl',
            save_recipe_data = '../data/out/recipe_ingname_list.json',
            has_recipe_data = False,
            recipe_data = '../data/out/recipe_ingname_list.json'):

        with open(foodon_to_root_file, 'rb') as f:
            foodon_to_root_dict = pickle.load(f)

        foodon_related_ings = defaultdict(lambda: set())
        ing_count = defaultdict(lambda: 0)
        R2V = RecToVec(graph=rdflib.ConjunctiveGraph(), food_index_file=index_dict_file)
        ing_cooc_counts = lil_matrix((len(R2V.food_index.keys()), len(R2V.food_index.keys())))
        raw_ings_in_recipes = []
        if not has_recipe_data:
            for data_files in foodkg_data_files:
                print(data_files)
                g = rdflib.ConjunctiveGraph()
                for foodon_link_file in food_link_files:
                    g.parse(foodon_link_file, format='ttl')
                g.parse(data_files, format='ttl')
                R2V = RecToVec(graph=g, food_index_file=index_dict_file)
                print('loaded')

                valid_foodon_items = set(item[1] for item in R2V.ing_to_foodon_dict.items())
                for foodon_food in valid_foodon_items:
                    # print(foodon_food)
                    path_items = foodon_to_root_dict.get(foodon_food, [])
                    for item in path_items:
                        if item in valid_foodon_items:
                            foodon_related_ings[foodon_food].add(item)
                            # foodon_related_ings[item].add(foodon_food) #v1 used this line, v3 didn't

                print('foodon food item related dict : ', len(foodon_related_ings.keys()))

                print(ing_cooc_counts.shape)

                start = time.time()
                num_recs = 0
                for recipe in g.subjects(rdflib.namespace.RDF['type'], rdflib.URIRef('http://idea.rpi.edu/heals/kb/recipe')):
                    raw_ings, _ = R2V.get_recipe_ingredients_and_weights(recipe_uri=recipe)
                    if not raw_ings:
                        continue
                    raw_ings_in_recipes.append([raw_ing[44:] for raw_ing in raw_ings])

                    # convert to foodon foods
                    ings = [R2V.ing_to_foodon_dict.get(ing, 0) for ing in raw_ings]
                    if 0 in ings:
                        continue

                    num_recs += 1
                    if num_recs%1000 == 0:
                        print(num_recs)

                    ings = list(ings)
                    ings_and_related = [foodon_related_ings[ing] for ing in ings] #v2 used just [ing], not convering to related ings
                    for i in range(len(ings)):
                        ing_set = ings_and_related[i]
                        for ing1 in ing_set:
                            ing_count[ing1] += 1
                            i_ind = R2V.index_for_ing(ing=ing1)
                            if i_ind is None:
                                continue
                            for j in range(i+1, len(ings)):
                                ing_set2 = ings_and_related[j]
                                for ing2 in ing_set2:
                                    j_ind = R2V.index_for_ing(ing=ing2)
                                    if j_ind is None:
                                        continue
                                    ing_cooc_counts[i_ind, j_ind] += 1
                                    ing_cooc_counts[j_ind, i_ind] += 1

                print('recipes: ', num_recs)
                print(time.time()-start)

            with open(save_recipe_data, 'w') as f:
                json.dump(raw_ings_in_recipes, f)

        else:
            foodkg_ns = rdflib.Namespace('http://idea.rpi.edu/heals/kb/ingredientname/')
            with open(recipe_data, 'r') as f:
                recipes = json.load(f)

            g = rdflib.ConjunctiveGraph()
            for data_files in food_link_files:
                print(data_files)
                for file in data_files:
                    g.parse(file, format='ttl')
            R2V = RecToVec(graph=g, food_index_file=index_dict_file)
            print('loaded')

            food_to_foodon = dict()
            for subj, obj in g.subject_objects(predicate=rdflib.URIRef('http://idea.rpi.edu/heals/kb/equivalentFoodOnClass')):
                food_to_foodon[subj] = obj

            valid_foodon_items = set(item[1] for item in food_to_foodon.items())

            for foodon_food in valid_foodon_items:
                path_items = foodon_to_root_dict.get(foodon_food, [])
                for item in path_items:
                    if item in valid_foodon_items:
                        foodon_related_ings[foodon_food].add(item)

            print('foodon food item related dict : ', len(foodon_related_ings.keys()))

            start = time.time()
            num_recs = 0
            for recipe in recipes:
                raw_ings = [foodkg_ns[ing] for ing in recipe]
                raw_ings_in_recipes.append([raw_ing[44:] for raw_ing in raw_ings])

                # convert to foodon foods
                ings = [food_to_foodon.get(ing, 0) for ing in raw_ings]
                if 0 in ings:
                    continue

                num_recs += 1
                if num_recs % 1000 == 0:
                    print(num_recs)

                ings = list(ings)
                ings_and_related = [[ing] for ing in ings]
                for i in range(len(ings)):
                    ing_set = ings_and_related[i]
                    for ing1 in ing_set:
                        ing_count[ing1] += 1
                        i_ind = R2V.index_for_ing(ing=ing1)
                        if i_ind is None:
                            continue
                        for j in range(i + 1, len(ings)):
                            ing_set2 = ings_and_related[j]
                            for ing2 in ing_set2:
                                j_ind = R2V.index_for_ing(ing=ing2)
                                if j_ind is None:
                                    continue
                                ing_cooc_counts[i_ind, j_ind] += 1
                                ing_cooc_counts[j_ind, i_ind] += 1

            print('recipes: ', num_recs)
            print(time.time() - start)

        ing_count = dict(ing_count)
        print('saving intermediate occurrence/co-occurrence data')
        with open(save_ocurrence_dict, 'wb') as f:
            pickle.dump(ing_count, f)
        with open(save_coocurrence_matrix, 'wb') as f:
            pickle.dump(ing_cooc_counts, f)

        def l2_norm(mat):
            return np.sqrt(np.sum(mat.multiply(mat), axis=1))

        R2V = RecToVec(graph=rdflib.ConjunctiveGraph(), food_index_file=index_dict_file)
        ing_cooc_counts = ing_cooc_counts.tocsr()
        divides = np.ones((ing_cooc_counts.shape[0], 1))
        ing_probs = ing_cooc_counts/divides
        ing_probs = csr_matrix(ing_probs)

        l2n = l2_norm(ing_probs)
        cosine_sim = ing_probs.dot(ing_probs.T) / (l2n.dot(l2n.T))

        ing_to_ing_cooc_sim_dict = dict()
        for ing1 in ing_count.keys():
            ing_to_ing_cooc_sim_dict[ing1] = dict()
            for ing2 in ing_count.keys():
                ing_to_ing_cooc_sim_dict[ing1][ing2] = cosine_sim[R2V.food_index[ing1], R2V.food_index[ing2]]

        print('saving ingredient cooccurrence similarity')
        with open(save_cooc_sim_dict, 'wb') as f:
            pickle.dump(ing_to_ing_cooc_sim_dict, f)
