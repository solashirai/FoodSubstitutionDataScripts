import rdflib
import json
import pickle

recipe_level = False
open_file = 'recipe_level_comment_content_with_keywords.pkl'

save_file = 'data/out/fooddotcom_review_sub_data.json'

food_link_files = ['../experiment_code/data/in/foodon-links-1.ttl']

ignore_foodkg_ing_strings = {
    'water', 'boiling water', 'cold water', 'liquid'
}
ing_ns = rdflib.Namespace('http://idea.rpi.edu/heals/kb/ingredientname/')

g = rdflib.Graph()
for file in food_link_files:
    g.parse(file, format='ttl')
print("files loaded")

food_to_foodon = dict()
relevant_food_names_as_str = set()
str_to_uri = dict()
for subj, obj in g.subject_objects(predicate=rdflib.URIRef('http://idea.rpi.edu/heals/kb/equivalentFoodOnClass')):
    food_to_foodon[subj] = obj
    str_split_name = str(subj)[44:]
    str_split_name = str_split_name.replace("%20", " ")
    if str_split_name not in ignore_foodkg_ing_strings:
        str_to_uri[str_split_name] = subj
        relevant_food_names_as_str.add(str_split_name)
print('foods with links: ', len(food_to_foodon.keys()))


raw_tups = []
with open(open_file, 'rb') as f:
    raw_data = pickle.load(f)
if recipe_level:
    raw_tups = [[tup[1]['source'].strip(), tup[1]['sub'].strip()] for tup in raw_data]
    recipe_tups = [tup[0] for tup in raw_data]
else:
    raw_tups = [[tup['source'].strip(), tup['sub'].strip()] for tup in raw_data]

found_source_names = set()
all_tups = []
for tup_ind, tups in enumerate(raw_tups):
    mod_name = []
    src_ing = tups[0]
    to_ing = tups[1]

    # set up src ing
    if src_ing[:4] == "the ":
        src_ing = src_ing[4:]
    src_ing = src_ing.replace(" ", "%20")
    src_ing = src_ing.lower()
    src_ing = ing_ns[src_ing]
    if src_ing in food_to_foodon.keys():
        # print(src_ing)
        found_source_names.add(src_ing)
        mod_name.append(src_ing)
    else:
        print(src_ing, ' not found')
        continue

    # set up to ing
    to_ing = to_ing.lower()
    to_ing = to_ing.replace(" teaspoons ", " ")
    to_ing = to_ing.replace(" teaspoon ", " ")
    to_ing = to_ing.replace(" cups ", " ")
    to_ing = to_ing.replace(" cup ", " ")
    to_ing = to_ing.replace(" tablespoons ", " ")
    to_ing = to_ing.replace(" tablespoon ", " ")
    matched_ings_to_foodkg = []
    for str_ings in relevant_food_names_as_str:
        if str_ings in to_ing:
            matched_ings_to_foodkg.append(str_ings)

    to_remove_matches = set()
    for matched_ing in matched_ings_to_foodkg:
        for matched_ing_2 in matched_ings_to_foodkg:
            if matched_ing == matched_ing_2:
                continue
            if matched_ing in matched_ing_2:
                to_remove_matches.add(matched_ing)
    for to_rem in to_remove_matches:
        matched_ings_to_foodkg.remove(to_rem)

    if len(matched_ings_to_foodkg) == 1:
        mod_name.append(str_to_uri[matched_ings_to_foodkg[0]])
        if recipe_level:
            all_tups.append((recipe_tups[tup_ind], mod_name[0], mod_name[1]))
        else:
            all_tups.append(tuple(mod_name))
    elif len(matched_ings_to_foodkg) == 0:
        print(src_ing, ':', to_ing)
    elif len(matched_ings_to_foodkg) > 1:
        print(src_ing, ':', to_ing, matched_ings_to_foodkg)

if recipe_level:
    all_tups = list(set([(tup[0], tup[1][44:].replace("%20", " "), tup[2][44:].replace("%20", " ")) for tup in all_tups]))
    all_tups = [{'recipeID':tup[0], 'fromIng': tup[1], 'toIng': tup[2]} for tup in all_tups]
else:
    all_tups = list(set([(tup[0][44:].replace("%20", " "), tup[1][44:].replace("%20", " ")) for tup in all_tups]))
    all_tups = [{'fromIng': tup[0], 'toIng': tup[1]} for tup in all_tups]
print('number of src ings: ', len(found_source_names))
print('simple match counts: ', len(all_tups))
# print('10 examples: ', all_tups[:10])

with open(save_file, 'w') as f:
    json.dump(all_tups, f)
