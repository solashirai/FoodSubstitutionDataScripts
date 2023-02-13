import rdflib
import pickle


class FoodSubclassPaths:

    def run(self,*,
            food_link_files = ['../data/in/foodon-links.trig'],
            food_index_file = '../data/out/food_index_dict.pkl',
            save_file = '../data/out/foodon_to_root_path.pkl',
            foodon_file = '../data/in/food_on.owl'):

        g = rdflib.ConjunctiveGraph()
        for input_file in food_link_files:
            g.parse(input_file, format='trig')
        foodon_graph = rdflib.Graph()
        foodon_graph.parse(foodon_file)#, format='ttl')

        class_count = foodon_graph.query("""
        prefix ns1: <http://www.w3.org/2002/07/owl#>
        prefix ns2: <http://idea.rpi.edu/heals/kb/> 
        prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> 
        prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> 
        prefix xml: <http://www.w3.org/XML/1998/namespace> 
        prefix xsd: <http://www.w3.org/2001/XMLSchema#> 
        SELECT ?food
        WHERE {
            ?food a ns1:Class .
        }
        """)
        counter = 0
        class_to_index_dict = dict()
        for res in class_count:
            class_to_index_dict[res.food] = counter
            counter += 1

        class_count = len(class_to_index_dict.keys())
        print('number of classes: ', class_count)

        #ns2:equivalentFoodOnClass
        q = g.query("""
        prefix ns2: <http://idea.rpi.edu/heals/kb/>
        prefix owl: <http://www.w3.org/2002/07/owl#>
        SELECT ?foodlink
        WHERE {
            ?subj owl:equivalentClass ?foodlink .
        }
        """)

        food_path_dict = dict()


        def get_path_items(graph, prev_subj):
            if prev_subj == rdflib.URIRef('http://purl.obolibrary.org/obo/FOODON_00001002'):
                return {prev_subj}

            to_return = {prev_subj}

            for obj in graph.objects(prev_subj, rdflib.namespace.RDFS['subClassOf']):
                if (obj, rdflib.namespace.RDF['type'], rdflib.namespace.OWL['Class']) in graph:
                    if obj in to_return:
                        continue
                    to_return = to_return.union(get_path_items(graph, obj))
            return to_return


        count = 0
        for res in q:
            food = res.foodlink
            if food not in class_to_index_dict.keys():
                class_to_index_dict[food] = len(class_to_index_dict)
            if food in food_path_dict.keys():
                continue
            pathset = get_path_items(foodon_graph, food)

            food_path_dict[food] = frozenset(pathset)

            count += 1
            if count % 50 == 0:
                print('completed ', count)

        print('finished, saving...')
        with open(save_file, 'wb') as f:
            pickle.dump(food_path_dict, f)

        with open(food_index_file, 'wb') as f:
            pickle.dump(class_to_index_dict, f)
