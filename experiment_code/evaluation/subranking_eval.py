import rdflib
import pickle
from collections import defaultdict
import json
import numpy as np


food_ns = rdflib.Namespace('http://purl.obolibrary.org/obo/')
IGNORE_INGS = {food_ns[ing] for ing in [
    'FOODON_00002221', #salt products
    'FOODON_03305008',
    'FOODON_03309467',
    'FOODON_03309954',
    'FOODON_03304059', #water
    'FOODON_03309928', #pepper
    'FOODON_03306739', #black pepper
    'FOODON_00001650', #black pepper food product
]}
food_link_files = ['../data/in/foodon-links-1.ttl']

substitution_data_files = [
    '../data/in/foodsubs_data.json',
    ]

foodon_superclasses_file = '../data/out/foodon_to_root_path.pkl'
ignored_ings = set()

ppmi_sim_file = '../data/out/foodon_ppmi_sim_dict.pkl'

cooc_sim_file = '../data/out/food_cooc_sim_dict.pkl'

word2vec_sim_file = '../data/out/w2v_ing_sim.pkl'
#
spacy_sim_file = '../data/out/spacy_ing_sim.pkl'



with open(cooc_sim_file, 'rb') as f:
    cooc_sim = pickle.load(f)
with open(ppmi_sim_file, 'rb') as f:
    ppmi_sim = pickle.load(f)
with open(word2vec_sim_file, 'rb') as f:
    word2vec_ing_sim = pickle.load(f)
with open(spacy_sim_file, 'rb') as f:
    spacy_ing_sim = pickle.load(f)
with open(foodon_superclasses_file, 'rb') as f:
    foodon_superclasses = pickle.load(f)


g = rdflib.Graph()
for file in food_link_files:
    g.parse(file, format='ttl')
food_to_foodon = dict()
test_foodon_ings = set()
for subj, obj in g.subject_objects(predicate=rdflib.URIRef('http://idea.rpi.edu/heals/kb/equivalentFoodOnClass')):
    food_to_foodon[subj] = obj
    test_foodon_ings.add(obj)


scraped_subs_tups = []
for substitution_data_file in substitution_data_files:
    with open(substitution_data_file, 'r') as f:
        data = json.load(f)
        print(substitution_data_file, len(data))
        scraped_subs_tups.extend(data)
        
srcings = set()
for tup in scraped_subs_tups:
    if rdflib.URIRef(tup[0]) in food_to_foodon.keys():
        if rdflib.URIRef(tup[1]) in food_to_foodon.keys():
            srcings.add(tup[0])
            srcings.add(tup[1])

print('relevant foodon foods: ', len(test_foodon_ings))
good_subs = 0
good_subs_from = set()
scraped_subs_dict = defaultdict(set)
scraped_subs_as_foodon_dict = defaultdict(set)
same_foodon_count = 0
unique_ings = set()
unique_foodon_ings = set()

for i in range(len(scraped_subs_tups)):
    scraped_subs_tups[i] = [rdflib.URIRef(scraped_subs_tups[i][0]), rdflib.URIRef(scraped_subs_tups[i][1])]
    rawing1 = rdflib.URIRef(scraped_subs_tups[i][0])
    rawing2 = rdflib.URIRef(scraped_subs_tups[i][1])

    ing1 = food_to_foodon.get(rawing1, 0)
    ing2 = food_to_foodon.get(rawing2, 0)
    if not ing1 or not ing2:
        if not ing1:
            ignored_ings.add(rawing1)
        if not ing2:
            ignored_ings.add(rawing2)
        continue
    if ing1 not in ppmi_sim.keys() or ing2 not in ppmi_sim.keys():
        if ing1 not in ppmi_sim.keys():
            ignored_ings.add(rawing1)
        if ing2 not in ppmi_sim.keys():
            ignored_ings.add(rawing2)
        continue
    if ing1 not in cooc_sim.keys() or ing2 not in cooc_sim.keys():
        if ing1 not in cooc_sim.keys():
            ignored_ings.add(rawing1)
        if ing2 not in cooc_sim.keys():
            ignored_ings.add(rawing2)
        continue
    if ing1 in test_foodon_ings and ing2 in test_foodon_ings and ing1 not in IGNORE_INGS and ing2 not in IGNORE_INGS:
        if rawing1 in spacy_ing_sim.keys() and rawing1 in word2vec_ing_sim.keys() and rawing2 in spacy_ing_sim.keys() and rawing2 in word2vec_ing_sim.keys():
            if ing1 != ing2 and rawing2 not in scraped_subs_dict[rawing1]:

                scraped_subs_dict[rawing1].add(rawing2)
                scraped_subs_as_foodon_dict[ing1].add(ing2)
                unique_ings.add(rawing1)
                unique_foodon_ings.add(ing1)
                unique_ings.add(rawing2)
                unique_foodon_ings.add(ing2)
        else:
            if rawing1 not in spacy_ing_sim.keys() or rawing1 not in word2vec_ing_sim.keys():
                ignored_ings.add(rawing1)
            if rawing2 not in spacy_ing_sim.keys() and rawing2 not in word2vec_ing_sim.keys():
                ignored_ings.add(rawing2)

print("ignored ings in sub data: ", len(ignored_ings))

scraped_subs_dict = dict(scraped_subs_dict)

print('unique ings: ', len(unique_ings))
print('unique foodon ings: ', len(unique_foodon_ings))

subpair_count = 0
for k in scraped_subs_dict.keys():
    subpair_count += len(scraped_subs_dict[k])
print('total substitutions pairs: ', subpair_count)


def get_simscore_ingrank_onlyss_multisamerank(from_ing, to_ing, opt, do_foodon_filtering):
    sim_dict = get_sim_dict(from_ing, opt)

    sorted_simscore = sorted(sim_dict[from_ing].items(), key=lambda item: item[1], reverse=True)

    rank = 0
    seen_foodon = set()
    target_to_foodon = food_to_foodon[to_ing]
    src_to_foodon = food_to_foodon[from_ing]

    for ind in sorted_simscore:
        at_ind = ind[0]
        score_at_ind = ind[1]
        at_ind_foodon = food_to_foodon[at_ind]
        if at_ind == from_ing:
            continue
        elif at_ind == to_ing or\
                ((opt == 3 or opt == 4) and at_ind_foodon == target_to_foodon):
            return rank, score_at_ind
        elif do_foodon_filtering and \
                (
                 at_ind_foodon in foodon_superclasses[src_to_foodon] or
                 src_to_foodon in foodon_superclasses[at_ind_foodon]):
            continue
        else:
            rank += 1
            seen_foodon.add(at_ind_foodon)
    return rank, score_at_ind

def get_sim_dict(from_ing, opt):
    sim_dict = dict()
    sim_dict[from_ing] = dict()
    if opt == 0:
        for ing in unique_ings:
            sim_dict[from_ing][ing] = (word2vec_ing_sim[from_ing][ing]) + \
                                      (spacy_ing_sim[from_ing][ing]**2) + \
                                      0.5*(cooc_sim[food_to_foodon[from_ing]][food_to_foodon[ing]]**0.25) + \
                                      2*(ppmi_sim[food_to_foodon[from_ing]][food_to_foodon[ing]]**0.5)
    elif opt == 1:
        for ing in unique_ings:
            sim_dict[from_ing][ing] = word2vec_ing_sim[from_ing][ing]
    elif opt == 2:
        for ing in unique_ings:
            sim_dict[from_ing][ing] = spacy_ing_sim[from_ing][ing]
    elif opt == 3:
        for ing in unique_ings:
            sim_dict[from_ing][ing] = cooc_sim[food_to_foodon[from_ing]][food_to_foodon[ing]]
    elif opt == 4:
        for ing in unique_ings:
            sim_dict[from_ing][ing] = ppmi_sim[food_to_foodon[from_ing]][food_to_foodon[ing]]
    return sim_dict

def mrr_map_new(opt, do_foodon_filtering):
    rank_scores = []
    ave_p = []
    in_top_5 = 0
    in_top_10 = 0
    print('number of ings: ',len(scraped_subs_dict.keys()))

    for fromt in scraped_subs_dict.keys():
        relevant_ranks = []
        min_rank = 9999999999999999
        for asdf in scraped_subs_dict[fromt]:
            rank = get_simscore_ingrank_onlyss_multisamerank(fromt, asdf, opt, do_foodon_filtering=do_foodon_filtering)[0]+1
            relevant_ranks.append(rank)
            if fromt == 'potato':
                print(asdf, rank)
            if rank < min_rank:
                min_rank = rank
        rank = min_rank

        rank_scores.append(1.0/rank)
        if min_rank <= 5:
            in_top_5 += 1
        if min_rank <= 10:
            in_top_10 += 1

        precisions = []
        for rank in relevant_ranks:
            good_docs = len([r for r in relevant_ranks if r <= rank])
            precisions.append(good_docs/rank)
        if len(precisions) == 0:
            precisions = [0]
        ave_p.append(np.mean(precisions))

    print('mean reciprocal rank: ', np.mean(rank_scores))
    print('recallrate at 5: ', in_top_5/len(scraped_subs_dict.keys()))
    print('recallrate at 10: ', in_top_10/len(scraped_subs_dict.keys()))
    print('mean average precision: ', np.mean(ave_p))
    print('formatted')
    print(round(np.mean(ave_p), 3),' & ',round(np.mean(rank_scores), 3),' & ',round(in_top_5/len(scraped_subs_dict.keys()), 3),' & ',round(in_top_10/len(scraped_subs_dict.keys()), 3))
    return round(np.mean(ave_p), 3)

print("0")
print('filtering...')
mrr_map_new(opt=0, do_foodon_filtering=True)

print("1")
print('filtering...')
mrr_map_new(opt=1, do_foodon_filtering=True)

print("2")
print('filtering...')
mrr_map_new(opt=2, do_foodon_filtering=True)

print("3")
print('filtering...')
mrr_map_new(opt=3, do_foodon_filtering=True)

print("4")
print('filtering...')
mrr_map_new(opt=4, do_foodon_filtering=True)