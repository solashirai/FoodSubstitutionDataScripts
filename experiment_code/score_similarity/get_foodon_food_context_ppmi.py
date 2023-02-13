import rdflib
import pickle
from collections import defaultdict
import numpy as np
import time
import json
from scipy.sparse import csr_matrix, lil_matrix, dok_matrix
from .rec_to_vec import RecToVec

# set up namespaces
food_ns = rdflib.Namespace('http://purl.obolibrary.org/obo/')
foodkg_ns = rdflib.Namespace('http://idea.rpi.edu/heals/kb/ingredientname/')

# some foodon ingredients that we want to ignore in our analysis - namely, salt, peper, and water
IGNORE_INGS = {food_ns[ing] for ing in [
    'FOODON_00002221',  # salt products
    'FOODON_03305008',
    'FOODON_03309467',
    'FOODON_03309954',
    'FOODON_03304059',  # water
    'FOODON_03309928',  # pepper
    'FOODON_03306739',  # black pepper
    'FOODON_00001650',  # black pepper food product
    'FOODON_00001002',  # parent class for all 'food products'
]}

class FoodPPMISimScore:

    def run(self, *,
            foodon_to_root_file = '../data/out/foodon_to_root_path.pkl',
            recipes_file = '../data/out/recipe_ingname_list.json',
            index_dict_file = '../data/out/food_index_dict.pkl',
            food_link_files = ['../data/in/foodon-links.trig'],
            save_ppmi_dict = '../data/out/foodon_ppmi_sim_dict.pkl'):

        with open(foodon_to_root_file, 'rb') as f:
            foodon_to_root_dict = pickle.load(f)

        ################

        g = rdflib.ConjunctiveGraph()
        for file in food_link_files:
            g.parse(file, format='trig')
        food_to_foodon = dict()

        for subj, obj in g.subject_objects(predicate=rdflib.URIRef('http://www.w3.org/2002/07/owl#equivalentClass')):#rdflib.URIRef('http://idea.rpi.edu/heals/kb/equivalentFoodOnClass')):
            food_to_foodon[subj] = obj

        valid_foodon_items = set(item[1] for item in food_to_foodon.items()) - IGNORE_INGS
        foodon_super_to_root = defaultdict(lambda: set())
        for foodon_food in valid_foodon_items:
            path_items = foodon_to_root_dict.get(foodon_food, [])
            for item in path_items:
                if item in valid_foodon_items:
                    foodon_super_to_root[foodon_food].add(item)
        foodon_super_to_root = {key: frozenset(val) for key, val in foodon_super_to_root.items()}

        R2V = RecToVec(graph=rdflib.ConjunctiveGraph(), food_index_file=index_dict_file)

        with open(recipes_file, 'r') as f:
            recipe_list = json.load(f)

        print("files loaded")

        ing_context_ocurrences = defaultdict(lambda: defaultdict(lambda: 0))

        ing_occurrence_count = defaultdict(lambda: 0)
        context_ocurrences = defaultdict(lambda: 0)
        unique_contexts = set()
        relevant_foods = set()
        ind_to_context = []
        completed_recipes = 0
        start = time.time()
        for recipe in recipe_list:
            ings = [food_to_foodon.get(foodkg_ns[ing], 0) for ing in recipe]

            if 0 in ings:
                continue

            ings_set = set(ings) - IGNORE_INGS
            for ing in ings_set:
                context_ings = frozenset(ings_set-{ing})
                unique_contexts.add(context_ings)
                context_ocurrences[context_ings] += 1

                super_foods = foodon_super_to_root[ing]
                for related_ing in super_foods:  # superclasses in super_foods also includes the ing itself
                    relevant_foods.add(related_ing)
                    ing_context_ocurrences[related_ing][context_ings] += 1
                    ing_occurrence_count[related_ing] += 1

            completed_recipes+=1
            if completed_recipes%10000 == 0:
                print(completed_recipes, ' - time - ', time.time()-start)
                start = time.time()

        total_context_count = len(unique_contexts)
        print('unique contexts: ', total_context_count)
        print("setting up computing ppmi, using foodon relations")

        ind_to_context = []
        context_to_ind = dict()
        for c in context_ocurrences.keys():
            context_to_ind[c] = len(ind_to_context)
            ind_to_context.append(c)
        ind_to_ing = []

        ing_to_context_ppmi = lil_matrix((len(R2V.food_index), total_context_count))

        finished_count = 0
        for ing in relevant_foods:
            ing_index = R2V.index_for_ing(ing)
            if ing_index is None:
                continue
            ing_contexts = ing_context_ocurrences[ing]
            ing_context_mat = ing_context_ocurrences.get(ing, None)
            if ing_context_mat is None:
                continue

            ing_occ_count = ing_occurrence_count[ing]

            ing_contexts_as_set = frozenset(ing_contexts.keys())
            for c in ing_contexts_as_set:
                i = context_to_ind[c]
                # # V1 and V2
                ppmi = max(0, np.log10((ing_contexts[c]*total_context_count)/(ing_occ_count*context_ocurrences[c]))*
                           np.sqrt(max(ing_occ_count, context_ocurrences[c])))
                ing_to_context_ppmi[ing_index,i] = ppmi

                # v4
                # ing_to_context_ppmi[ing_index, i] = ing_contexts[c]

            finished_count += 1
            if finished_count % 100 == 0 or finished_count < 5:
                print('getting ppmi, completed ', finished_count)
            ing_context_ocurrences[ing] = None

        ing_to_context_ppmi = ing_to_context_ppmi.tocsr()
        ing_to_ing_ppmi_sim = dict()
        print("converting to cosine sim...")
        finished_count = 0
        def l2_norm(mat):
            return np.sqrt(np.sum(mat.multiply(mat), axis=1))
        l2n = l2_norm(ing_to_context_ppmi)

        cosine_sim = ing_to_context_ppmi.dot(ing_to_context_ppmi.T) / (l2n.dot(l2n.T))

        for ing1 in relevant_foods:
            ing_index = R2V.index_for_ing(ing)
            if ing_index is None:
                continue
            ing_to_ing_ppmi_sim[ing1] = dict()
            irow = ing_to_context_ppmi[ing_index]

            for ing2 in relevant_foods:
                ing_to_ing_ppmi_sim[ing1][ing2] = cosine_sim[R2V.food_index[ing1], R2V.food_index[ing2]]

            finished_count += 1
            if finished_count % 100 == 0 or finished_count < 5:
                print('completed count: ', finished_count)

        print('finished, saving output')

        with open(save_ppmi_dict, 'wb') as f:
            pickle.dump(ing_to_ing_ppmi_sim, f)
