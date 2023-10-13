import glob
import re

from rdflib import Graph, URIRef

IRI_BRACKET_PATTERN = re.compile(pattern='<.+>')
PREFIX_PATTERN = re.compile(pattern='([a-z]+-[a-z]+)\s*:(\s*<.+>)')
IRI_PREFIX_PATTERN = re.compile(pattern='[a-z]+-[a-z]+\s*:\s*\w+')

def __get_simple_iris_from_rqg_transformation_script(rqg_transformation_script: str) -> set:
    iris_in_brackets = set(IRI_BRACKET_PATTERN.findall(string=rqg_transformation_script))
    iris = set()
    for iri_in_bracket in iris_in_brackets:
        iris.add(iri_in_bracket[1:-1])
    return iris
    
def __get_prefixed_iris_from_rqg_transformation_script(rqg_transformation_script: str) -> tuple:
    truncated_rqg_transformation_script = rqg_transformation_script
    prefix_definitions = set(PREFIX_PATTERN.findall(string=rqg_transformation_script))
    prefixed_iris = set(IRI_PREFIX_PATTERN.findall(string=rqg_transformation_script))
    iris = set()
    for prefix_definition in prefix_definitions:
        prefix = prefix_definition[0].strip()
        namespace_iri = (prefix_definition[1]).strip()[1:-1]
        for prefixed_iri in prefixed_iris:
            if prefixed_iri.startswith(prefix):
                iri = prefixed_iri.replace(prefix+':', namespace_iri)
                iris.add(iri)
        truncated_rqg_transformation_script = truncated_rqg_transformation_script.replace(namespace_iri, '')
        
    return iris, truncated_rqg_transformation_script

def check_rqg_transformation_scripts_in_folder(rqg_transformation_scripts_folder: str, ontology_location: str, resource_filter: str):
    rqg_file_contents = dict()
    rqg_resources = dict()
    for rqg_file_path in glob.glob(rqg_transformation_scripts_folder+'/**/*.rqg', recursive=True):
        with open(file=rqg_file_path) as rqg_file:
            rqg_file_content = rqg_file.read()
            rqg_file_contents[rqg_file_path] = rqg_file_content
            prefixed_iris, truncated_rqg_transformation_script = __get_prefixed_iris_from_rqg_transformation_script(rqg_transformation_script=rqg_file_content)
            simple_iris = __get_simple_iris_from_rqg_transformation_script(rqg_transformation_script=truncated_rqg_transformation_script)
            rqg_resources[rqg_file_path] = prefixed_iris.union(simple_iris)
            
    ontology = Graph()
    ontology.parse(ontology_location)
    ontology_resources = ontology.all_nodes()
    
    for rqg_file_path, iris in rqg_resources.items():
        for iri in iris:
            if resource_filter in iri:
                if URIRef(iri) not in ontology_resources:
                    print(rqg_file_path, iri)
    