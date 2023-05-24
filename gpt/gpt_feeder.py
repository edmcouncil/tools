import json
import re

from rdflib import Graph, RDF
from rdflib.resource import Resource
from rdflib.term import Node

from constants import PROMPT_SEPARATOR, COMPLETION_SEPARATOR, LABELS_PROPERTY, DEFINITIONS_PROPERTY, MEANS_COPULA
from gpt.sw_regexes import REGEX_MAP


def get_finetune_json_from_sw_types(ontology: Graph, sw_types: list, ontology_file_text: str) -> str:
    finetune_json = str()
    for sw_type in sw_types:
        finetune_json = get_finetune_json_from_sw_type(ontology=ontology, sw_type=sw_type, finetune_json=finetune_json, ontology_file_text=ontology_file_text)
    return finetune_json

def get_finetune_json_from_sw_type(ontology: Graph, sw_type: Node, finetune_json: str, ontology_file_text: str) -> str:
    regex = REGEX_MAP.get(sw_type)
    owl_descriptions = regex.findall(string=ontology_file_text)
    owl_descriptions_map = dict()
    for owl_description in owl_descriptions:
        owl_descriptions_map[owl_description[1]] = owl_description[0]
    resources_of_type = set(ontology.subjects(predicate=RDF.type, object=sw_type))
    for resource in resources_of_type:
        finetune_json = get_finetune_json_from_resource(ontology=ontology,resource=resource,finetune_json=finetune_json, owl_descriptions_map=owl_descriptions_map)
    return finetune_json
    
def get_finetune_json_from_resource(ontology: Graph, resource: Node, finetune_json: str, owl_descriptions_map: dict) -> str:
    text = __get_annotations_text_for_resource(ontology=ontology, resource=resource)
    axioms_text = __get_axioms_text_for_resource(resource=resource, owl_descriptions_map=owl_descriptions_map)
    if len(text) == 0 or len(axioms_text) == 0:
        return finetune_json
    prompt_text = text + PROMPT_SEPARATOR
    completion_text = ' ' + axioms_text + COMPLETION_SEPARATOR
    finetune_json += json.dumps({'prompt': prompt_text, 'completion': completion_text})
    finetune_json += '\n'
    return finetune_json
    
def __get_annotations_text_for_resource(ontology: Graph, resource: Node) -> str:
    annotations_text = str()
    labels = list(ontology.objects(subject=resource, predicate=LABELS_PROPERTY))
    if not len(labels) == 1:
        return annotations_text
    label = str(labels[0])
    definitions = list(ontology.objects(subject=resource, predicate=DEFINITIONS_PROPERTY))
    if not len(definitions) == 1:
        return annotations_text
    definition = str(definitions[0])
    annotations_text = label + MEANS_COPULA + definition
    return annotations_text

def __get_axioms_text_for_resource(resource: Node, owl_descriptions_map: dict) -> str:
    if str(resource) in owl_descriptions_map:
        axioms_text = owl_descriptions_map[str(resource)]
        axioms_text = re.sub(pattern=re.compile('\t|\r|\n'), string=axioms_text,repl='')
        axioms_text = re.sub(pattern=re.compile('\s+'), string=axioms_text, repl=' ')
        return axioms_text
    return str()



