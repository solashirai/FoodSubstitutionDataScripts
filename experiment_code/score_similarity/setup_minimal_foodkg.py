import rdflib


def make_min(in_files, out_file):
    # cut down on data from foodkg that's unnecessary for this repo's code, since the amount of
    # extra triples makes loading very slow
    g = rdflib.ConjunctiveGraph()
    min_g = rdflib.Graph()

    print("loading")
    for f in in_files:
        g.parse(f, format='trig')
    
    print("start processing")
    recipe_ns = rdflib.Namespace("http://idea.rpi.edu/heals/kb/")
    TYPE_RECIPE = recipe_ns["recipe"]
    TYPE_INGUSE = recipe_ns["ingredientuse"]
    TYPE_INGNAME = recipe_ns["ingredientname"]
    PRED_USES = recipe_ns["uses"]
    PRED_INGNAME = recipe_ns["ing_name"]

    for t in g.triples((None, None, TYPE_RECIPE)):
        min_g.add(t)
    for t in g.triples((None, None, TYPE_INGUSE)):
        min_g.add(t)
    for t in g.triples((None, None, TYPE_INGNAME)):
        min_g.add(t)
    for t in g.triples((None, PRED_USES, None)):
        min_g.add(t)
    for t in g.triples((None, PRED_INGNAME, None)):
        min_g.add(t)

    print("saving minimal kg")
    min_g.serialize(out_file, format='nt')
