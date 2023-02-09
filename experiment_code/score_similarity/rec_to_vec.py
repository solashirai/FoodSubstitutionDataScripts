import pickle
import rdflib
import numpy as np
from typing import List
from scipy.sparse import csr_matrix, vstack

food_ns = rdflib.Namespace('http://idea.rpi.edu/heals/kb/')


class RecToVec:

    def __init__(self, graph,
                 food_path_file:str='../data/out/foodon_to_root_path.pkl',
                 food_index_file:str='../data/out/food_index_dict.pkl'):
        with open(food_path_file, 'rb') as f:
            self.food_path = pickle.load(f)
        with open(food_index_file, 'rb') as f:
            self.food_index = pickle.load(f)
        self.vector_shape = (1, len(self.food_index.keys()))
        self.graph = graph
        self.ing_to_foodon_dict = dict()
        self.ing_order = []
        self.foodon_ing_order = []
        for foodkg_food in graph.subjects(predicate=rdflib.namespace.RDF['type'], object=food_ns['ingredientname']):
            if foodkg_food is not None:
                equiv_food = graph.value(subject=foodkg_food, predicate=rdflib.URIRef('http://www.w3.org/2002/07/owl#equivalentClass'))#food_ns['equivalentFoodOnClass'])
                if equiv_food:
                    self.ing_to_foodon_dict[foodkg_food] = equiv_food
                    if equiv_food not in self.foodon_ing_order:
                        self.foodon_ing_order.append(equiv_food)
            self.ing_order.append(foodkg_food)

    def get_recipe_ingredients_and_weights(self, recipe_uri, unweighted=False, only_foodon_classes:bool=False):
        ing_uses = [ing_use for ing_use in self.graph.objects(recipe_uri, food_ns['uses'])]
        ing_names = []
        total_grams = 0
        use_grams = []
        if len(ing_uses) == 0:
            return None, None
        for ing_use in ing_uses:
            ing_name = self.graph.value(subject=ing_use, predicate=food_ns['ing_name'])
            if only_foodon_classes:
                foodon_eq = self.ing_to_foodon_dict.get(ing_name, 0)
                if foodon_eq:
                    ing_names.append(foodon_eq)
                else:
                    return None, None
            else:
                ing_names.append(ing_name)

            gram_quant = self.graph.value(subject=ing_use, predicate=food_ns['ing_computed_gram_quantity'])
            if gram_quant:
                use_grams.append(gram_quant.value)
                total_grams += gram_quant.value
            else:
                use_grams.append(1.0)
                total_grams += 1.0

        weights = []
        for ing_index, _ in enumerate(ing_uses):
            if unweighted:
                prop = 1 / len(ing_uses)
            else:
                prop = use_grams[ing_index] / total_grams
            weights.append(prop)
        return ing_names, weights

    def convert_recipe_to_vector(self, recipe_uri, unweighted=False, only_foodon_classes:bool = False):
        ing_names, weights = self.get_recipe_ingredients_and_weights(recipe_uri=recipe_uri, unweighted=unweighted, only_foodon_classes=only_foodon_classes)
        if not ing_names:
            return None

        return self.convert_ing_uses_to_vector(ings=ing_names, weights=weights)

    def convert_ing_uses_to_vector(self, ings: List[rdflib.URIRef], weights: List[float], using_path=True):
        recipe_vec = np.zeros(shape=self.vector_shape)
        for ing_index, ing in enumerate(ings):
            ing_weight = weights[ing_index]

            food_index = self.food_index[ing]
            if self.using_ic:
                recipe_vec[0, food_index] += ing_weight * self.food_to_ic.get(ing, 1)
            else:
                recipe_vec[0, food_index] += ing_weight

            if using_path:
                use_path = self.food_path.get(self.ing_to_foodon_dict.get(ing, ing), [])
                for path_food in use_path:
                    food_index = self.food_index[path_food]

                    recipe_vec[0, food_index] += ing_weight

        return recipe_vec

    def ing_at_index(self, index):
        return self.ing_order[index]

    def index_for_ing(self, ing):
        return self.food_index[ing]

    def create_substitution_matrix(self, ings: List[rdflib.URIRef], weights: List[float],
                                   to_remove_ing: rdflib.URIRef, to_remove_wt: float, only_foodon_classes=False):
        base_vec = self.convert_ing_uses_to_vector(ings=ings, weights=weights)
        remove_vec = self.convert_ing_uses_to_vector(ings=[to_remove_ing], weights=[to_remove_wt])
        context_vec = base_vec - remove_vec

        substitution_recipe_matrix = []
        if only_foodon_classes:
            for ing in self.foodon_ing_order:
                sub_vec = context_vec + self.convert_ing_uses_to_vector(ings=[ing], weights=[to_remove_wt])
                substitution_recipe_matrix.append(csr_matrix(sub_vec))
        else:
            for ing in self.ing_order:
                sub_vec = context_vec + self.convert_ing_uses_to_vector(ings=[ing], weights=[to_remove_wt])
                substitution_recipe_matrix.append(csr_matrix(sub_vec))

        stacked_matrix = vstack(substitution_recipe_matrix)

        return stacked_matrix
