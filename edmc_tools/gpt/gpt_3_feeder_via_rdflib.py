import json

from rdflib import Graph, RDFS, SKOS, URIRef, RDF, OWL, Namespace

from constants import IS, IS_A

graph = Graph()
graph.bind("owl", OWL)
graph.bind("rdf", RDF)
graph.bind("rdfs", RDFS)
graph.bind("skos", SKOS)
graph.parse(r'/Users/pawel.garbacz/Documents/edmc/python/projects/edmc_tools/resources/dev.fibo-quickstart.ttl')
json_text = str()
for resource, predicate, object in graph:
    types = list(graph.objects(subject=resource, predicate=RDF.type))
    if OWL.Class in types:
        labels = list(graph.objects(subject=resource, predicate=RDFS.label))
        definitions = list(graph.objects(subject=resource, predicate=SKOS.definition))
        explanatoryNotes = list(graph.objects(subject=resource, predicate=URIRef('https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/explanatoryNote')))
        examples = list(graph.objects(subject=resource, predicate=SKOS.example))
        if len(labels) > 0 and len(definitions) > 0 and (len(explanatoryNotes) > 0 and len(examples) > 0):
            if definitions[0].startswith('a ') or definitions[0].startswith('an ') or definitions[0].startswith('the '):
                copula = IS
            else:
                copula = IS_A
            human_readable_text = labels[0].capitalize() + copula + definitions[0] + '.'
            human_readable_text += ' ' + ' '.join(explanatoryNotes)
            human_readable_text += ' ' + ' '.join(examples)
            prompt_text = human_readable_text + '###'
            resource_graph = Graph()
            resource_graph.bind("owl", OWL)
            resource_graph.bind("rdf", RDF)
            resource_graph.bind("rdfs", RDFS)
            resource_graph.bind("skos", SKOS)
            resource_graph.bind('av', Namespace('https://spec.edmcouncil.org/fibo/ontology/FND/Utilities/AnnotationVocabulary/'))
            for resource_predicate, resource_object in graph.predicate_objects(subject=resource):
                resource_graph.add((resource, resource_predicate, resource_object))
            completion_text = ' ' + resource_graph.serialize() + '|||'
            json_text += json.dumps({'prompt': prompt_text, 'completion': completion_text})
            json_text += '\n'
            # print(json_text)
gpt_fine_tune_file = open(file='gpt_fine_tune_file.jsonl', mode='w', encoding='UTF-8')
gpt_fine_tune_file.write(json_text)
gpt_fine_tune_file.close()
    