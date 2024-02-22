import json
import os
import subprocess
import time
import more_itertools
from more_itertools import powerset

from rdflib import Graph, RDF, OWL, URIRef

owl_constraint_types = \
    {
        OWL.qualifiedCardinality,
        OWL.minQualifiedCardinality,
        OWL.maxQualifiedCardinality,
        OWL.someValuesFrom,
        OWL.allValuesFrom,
        OWL.hasValue
    }

ontology = Graph()
ontology.parse('AboutFIBODev.ttl')
print('Full ontology has', len(ontology), 'triples')

profiling_results = dict()
consistency_results = dict()

owl_constraint_types_powerset = list(powerset(owl_constraint_types))
owl_constraint_types_powerset = sorted(owl_constraint_types_powerset, key=lambda x: len(x), reverse=True)
for owl_constraint_types_subset in owl_constraint_types_powerset:
    owl_profile_id = ' '.join(owl_constraint_types_subset)
    ontology = Graph()
    ontology.parse('AboutFIBODev.ttl')
    for (subject, predicate, object) in ontology:
        if predicate in owl_constraint_types_subset:
            for deleted_subject, deleted_object in set(ontology.subject_objects(predicate=predicate)):
                ontology.remove((deleted_subject, predicate, deleted_object))
                ontology.remove((deleted_object, predicate, deleted_subject))
    print('Ontology minus', owl_profile_id, 'has', len(ontology), 'triples')
    ontology.serialize('temp.ttl')
    
    log_file_path = 'log_' + owl_profile_id.replace('http://www.w3.org/2002/07/owl#','_').replace(' ', '') + '.txt'
    try:
        start = time.time()
        reasoning_process = \
                subprocess.Popen(
                    "java -jar ./onto-viewer-toolkit.jar --goal consistency-check --data " + 'temp.ttl' + " --output " + log_file_path,
                    shell=True)
        reasoning_process.wait(timeout=120)
        end = time.time()
        ontology_reasoning_time = end - start
        print(ontology_reasoning_time)
        profiling_results[owl_profile_id] = ontology_reasoning_time
    except Exception as ex:
        print(ex)
        profiling_results[owl_profile_id] = -1
    
    os.remove('temp.ttl')
    
with open('profiling_results.json', 'w') as profiling_results_file:
    json.dump(profiling_results, profiling_results_file, indent=4)
    
