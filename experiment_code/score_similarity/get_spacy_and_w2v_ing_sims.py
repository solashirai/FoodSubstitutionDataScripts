import en_core_web_lg
import json
import pickle
import numpy as np
import rdflib


class FoodEmbeddingSims:

    def run(self, *,
            spacy_savefile = '../data/out/spacy_ing_sim.pkl',
            w2v_savefile = '../data/out/w2v_ing_sim.pkl',
            substitution_data_file = '../data/in/foodsubs_data.json',
            w2v_file = '../data/in/r1m_word2vec/vocab.bin',
            food_link_files = ['../data/in/foodon-links-1.ttl']):

        g = rdflib.ConjunctiveGraph()
        for file in food_link_files:
            g.parse(file, format='ttl')
        food_to_foodon = dict()
        unique_foodon = set()
        for subj, obj in g.subject_objects(predicate=rdflib.URIRef('http://idea.rpi.edu/heals/kb/equivalentFoodOnClass')):
            food_to_foodon[subj] = obj
            unique_foodon.add(obj)


        relevant_foods = set()
        with open(substitution_data_file, 'r') as f:
            scraped_subs_tups = json.load(f)
        for i in range(len(scraped_subs_tups)):
            scraped_subs_tups[i] = [rdflib.URIRef(scraped_subs_tups[i][0]), rdflib.URIRef(scraped_subs_tups[i][1])]
            if scraped_subs_tups[i][0] in food_to_foodon.keys():
                relevant_foods.add(scraped_subs_tups[i][0])
            if scraped_subs_tups[i][1] in food_to_foodon.keys():
                relevant_foods.add(scraped_subs_tups[i][1])

        print('relevant foods: ', len(relevant_foods))

        print('ingredient names: ', len(food_to_foodon.keys()))
        print('foodon ingredients: ', len(unique_foodon))


        def l2_norm(mat):
            return np.sqrt(np.sum(np.multiply(mat, mat), axis=1))

        ###### SPACY
        ###############
        ############
        print("starting spacy")
        nlp = en_core_web_lg.load()

        ing_to_vec = np.zeros(shape=(len(relevant_foods), 300))
        print("getting vectors")
        ing_to_index = dict()
        ing_index = 0
        use_ings = set()
        for fromt_ing in relevant_foods:#food_to_foodon.keys():
            ing = fromt_ing[44:]
            ing_replaced = ing.replace("%20", " ")
            vec_parts = []
            doskip = False
            for token in nlp(ing_replaced):
                if np.sum(token.vector) == 0 or np.sum(token.vector) is np.nan:
                    print('ignoring ', ing)
                    doskip = True
                vec_parts.append(token.vector)
            if doskip:
                continue

            ing_to_index[fromt_ing] = ing_index
            ing_to_vec[ing_index, :] = np.mean(vec_parts, axis=0).reshape(1, -1)
            ing_index += 1
            use_ings.add(fromt_ing)
            if ing_index%1000 == 0:
                print(ing_index)

        l2n = l2_norm(ing_to_vec)

        print('getting sims for ', len(use_ings), ' ingreds')
        vec_ing_sim = dict()

        for ing in use_ings:
            index_1 = ing_to_index[ing]
            foodon_ing1 = food_to_foodon[ing]
            cosine_sim = np.dot(ing_to_vec[index_1].reshape(1, -1), ing_to_vec.T) / (l2_norm(ing_to_vec[index_1, :].reshape(1, -1))*(l2n))
            res_dict = dict()
            dist_list = []
            for ing2 in use_ings:
                index_2 = ing_to_index[ing2]
                foodon_ing2 = food_to_foodon[ing2]
                if ing == ing2:
                    res_dict[ing2] = 1
                elif ing2 in vec_ing_sim.keys():
                    res_dict[ing2] = vec_ing_sim[ing2][ing]
                else:
                    sim = cosine_sim[0, index_2]
                    res_dict[ing2] = sim
            vec_ing_sim[ing] = res_dict
            if len(vec_ing_sim.keys())%100 == 0:
                print(len(vec_ing_sim.keys()))

        print('finished setting up spacy sims, saving')

        with open(spacy_savefile, 'wb') as f:
            pickle.dump(vec_ing_sim, f)


        from gensim.models import KeyedVectors
        print("starting w2v")
        w2v_model = KeyedVectors.load_word2vec_format(w2v_file, binary=True)

        ing_to_vec = np.zeros(shape=(len(relevant_foods), 300))
        print("getting vectors")
        ing_to_index = dict()
        ing_index = 0
        use_ings = set()
        for fromt_ing in relevant_foods:#food_to_foodon.keys():
            ing = fromt_ing[44:]
            ing_replaced = ing.replace("%20", "_")
            if ing_replaced in w2v_model.vocab:
                ing_to_vec[ing_index, :] = w2v_model[ing_replaced].reshape(1, -1)
            else:
                if ing_replaced.lower() in w2v_model.vocab:
                    ing_to_vec[ing_index, :] = w2v_model[ing_replaced.lower()].reshape(1, -1)
                elif ing_replaced[0].upper()+ing_replaced[1:] in w2v_model.vocab:
                    ing_to_vec[ing_index, :] = w2v_model[ing_replaced[0].upper()+ing_replaced[1:]].reshape(1, -1)
                else:
                    vec_parts = []
                    ing_parts = ing_replaced.split("_")
                    doskip = False
                    for ing_part in ing_parts:
                        if ing_part in w2v_model.vocab:
                            vec_parts.append(w2v_model[ing_part])
                        else:
                            if ing_part.lower() in w2v_model.vocab:
                                vec_parts.append(w2v_model[ing_part.lower()])
                                #print(ing_part, " in ", ing, "! lower")
                            elif ing_part[0].upper()+ing_part[1:] in w2v_model.vocab:
                                vec_parts.append(w2v_model[ing_part[0].upper()+ing_part[1:]])
                            else:
                                print('ignoring ', fromt_ing)
                                doskip = True
                                continue
                    if doskip:
                        continue
                    if len(vec_parts) != 0:
                        vec = np.array(vec_parts)
                        vec = np.mean(vec_parts, axis=0)
                        ing_to_vec[ing_index, :] = vec.reshape(1, -1)
            ing_to_index[fromt_ing] = ing_index
            ing_index += 1
            use_ings.add(fromt_ing)
            if ing_index%1000 == 0:
                print(ing_index)

        l2n = l2_norm(ing_to_vec)

        print('getting sims for ', len(use_ings), ' ings')
        vec_ing_sim = dict()

        for ing in use_ings:
            index_1 = ing_to_index[ing]
            foodon_ing1 = food_to_foodon[ing]
            cosine_sim = np.dot(ing_to_vec[index_1].reshape(1, -1), ing_to_vec.T) / (l2_norm(ing_to_vec[index_1, :].reshape(1, -1))*(l2n))
            res_dict = dict()
            dist_list = []
            for ing2 in use_ings:
                index_2 = ing_to_index[ing2]
                foodon_ing2 = food_to_foodon[ing2]
                if ing == ing2:
                    res_dict[ing2] = 1
                elif ing2 in vec_ing_sim.keys():
                    res_dict[ing2] = vec_ing_sim[ing2][ing]
                else:
                    sim = cosine_sim[0, index_2]
                    res_dict[ing2] = sim
            vec_ing_sim[ing] = res_dict
            if len(vec_ing_sim.keys())%100 == 0:
                print(len(vec_ing_sim.keys()))

        print('finished setting up w2v sims, saving')

        with open(w2v_savefile, 'wb') as f:
            pickle.dump(vec_ing_sim, f)
