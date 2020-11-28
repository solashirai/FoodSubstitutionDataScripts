import json
import re
import rdflib
import spacy
from collections import defaultdict

nlp = spacy.load('en_core_web_lg')

chunks_file = 'manually_corrected_subs_webcontent_chunks.json'

foodkg_links_file = 'foodon-links-1.ttl'

with open(chunks_file, 'r') as f:
    data = json.load(f)

subs_from_to_extracted = []
for row in data:
    from_split = row[1].split("=")
    from_subs = [ing.lower().replace("\xa0", "") for ing in from_split]
    for i in range(len(from_subs)):
        if from_subs[i].find("(") > 0:
            from_subs[i] = from_subs[i][:from_subs[i].find("(")]
    from_subs = [" ".join(ing.split(" ")).strip() for ing in from_subs]
    from_subs = [" ".join([w.lemma_ for w in nlp(ing)]) for ing in from_subs if ing]

    to_split = row[2].split("OR")
    to_subs = [ing.lower().replace("\xa0", "").replace("-", " ") for ing in to_split]
    for i in range(len(to_subs)):
        if to_subs[i].find("(") > 0:
            leftb = to_subs[i].find("(")
            rightb = to_subs[i].find(")")
            to_subs[i] = to_subs[i][:leftb] + to_subs[i][rightb+1:]
    to_subs = [" ".join([w for w in ing.split(" ") if w]).strip() for ing in to_subs]
    to_subs = [" ".join([w.lemma_ for w in nlp(ing)]) for ing in to_subs if ing]

    subs_from_to_extracted.append((from_subs, to_subs))

print(len(subs_from_to_extracted))


ingstr_to_inguri = defaultdict(list)
G = rdflib.ConjunctiveGraph()

G.parse(foodkg_links_file, format='ttl')
ing_quer = G.query("""
prefix recipe-kb: <http://idea.rpi.edu/heals/kb/>
prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?ingname
WHERE {{
    ?ingname ?p ?o.
}}
""")

for res in ing_quer:
    name = res.ingname
    name = name[44:]
    name = name.replace("%20", " ")
    ingstr_lem = " ".join([w.lemma_ for w in nlp(name)])
    ingstr_to_inguri[ingstr_lem].append(res.ingname)



uri_to_uri_list = []
for ft_tup in subs_from_to_extracted:
    from_ings = ft_tup[0]
    to_ings = ft_tup[1]
    to_uris = [uri for ing in to_ings for uri in ingstr_to_inguri.get(ing, [])]
    for ing in from_ings:
        from_uris = ingstr_to_inguri.get(ing, [])
        for furi in from_uris:
            for turi in to_uris:
                uri_to_uri_list.append((furi, turi))
print(len(uri_to_uri_list))
with open('uri_foodsubs_dataset.json', 'w') as f:
    json.dump(uri_to_uri_list, f)

ing_to_ing_validuri_list = []
for ft_tup in subs_from_to_extracted:
    print(ft_tup)
    from_ings = {ing.replace(" - ", "-") for ing in ft_tup[0] if ingstr_to_inguri.get(ing, '')}
    to_ings = {ing for ing in ft_tup[1] if ingstr_to_inguri.get(ing, '')}
    for ing in from_ings:
        for to_ing in to_ings:
            ing_to_ing_validuri_list.append((ing, to_ing))
print(len(ing_to_ing_validuri_list))
with open('string_foodsubs_dataset.json', 'w') as f:
    json.dump(ing_to_ing_validuri_list, f)
