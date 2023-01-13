import os

from rdflib import Graph, OWL, RDF, RDFS
from rdflib.term import URIRef, Literal

from compare.comparision_config import ComparisionConfig
from json_helpers.json_serialiser import save_dict_as_json_file, save_dict_as_table_file
from owl_helpers.resource_identifiers import identify_resource

COUNT_SUFFIX = 'count'
KEY_1_MINUS_2 = 'left and not right'
KEY_2_MINUS_1 = 'right and not left'
KEY_1_AND_2 = 'both right and left'
KEY_1_MINUS_2_COUNT = KEY_1_MINUS_2 + ' ' + COUNT_SUFFIX
KEY_2_MINUS_1_COUNT = KEY_2_MINUS_1 + ' ' + COUNT_SUFFIX
KEY_1_AND_2_COUNT = KEY_1_AND_2 + ' ' + COUNT_SUFFIX
DIFF_RESOURCES_FOLDER = 'different_resources'
DIFF_AXIOMS_FOLDER = 'different_axioms_for_same_subjects'
DIFF_RESOURCES_JSON_FILE_NAME = 'different_resources.json'
DIFF_AXIOMS_JSON_FILE_NAME = 'different_axioms_for_same_subjects.json'
DIFF_RESOURCES_EXCEL_FILE_NAME = 'different_resources.xlsx'
DIFF_AXIOMS_EXCEL_FILE_NAME = 'different_axioms_for_same_subjects.xlsx'


def compare_ontologies(ontology_1_location: str, ontology_2_location: str, results_folder_path: str, verbose=False):
    ontology_comparison_basis_prefix = str()
    ontology_1 = Graph()
    if len(ontology_1_location) > 0:
        ontology_1.parse(ontology_1_location)
        ontology_comparison_basis_prefix = ontology_1_location.split(os.sep)[-1]
    ontology_2 = Graph()
    if len(ontology_2_location) > 0:
        ontology_2.parse(ontology_2_location)
        ontology_comparison_basis_prefix = ontology_2_location.split(os.sep)[-1]
    ontology_comparison_prefix, ontology_comparison_basis_extension = os.path.splitext(ontology_comparison_basis_prefix)
    
    config = ComparisionConfig(verbose=verbose)
    
    diff_resources = compare_ontological_resources(ontology_1, ontology_2, config)
    if len(diff_resources) > 0:
        save_dict_as_json_file(
            dicts=diff_resources,
            output_folder=os.path.join(results_folder_path, DIFF_RESOURCES_FOLDER),
            json_file_name=ontology_comparison_prefix +'_' + DIFF_RESOURCES_JSON_FILE_NAME)
        save_dict_as_table_file(
            dicts=diff_resources,
            output_folder=os.path.join(results_folder_path, DIFF_RESOURCES_FOLDER),
            table_file_name=ontology_comparison_prefix + '_' + DIFF_RESOURCES_EXCEL_FILE_NAME)

    diff_axioms = compare_axioms_for_same_subjects(ontology_1, ontology_2, config)
    if len(diff_axioms) > 0:
        save_dict_as_json_file(
            dicts=diff_axioms,
            output_folder=os.path.join(results_folder_path, DIFF_AXIOMS_FOLDER),
            json_file_name=ontology_comparison_prefix + '_' + DIFF_AXIOMS_JSON_FILE_NAME)
        save_dict_as_table_file(
            dicts=diff_axioms,
            output_folder=os.path.join(results_folder_path, DIFF_AXIOMS_FOLDER),
            table_file_name=ontology_comparison_prefix + '_' + DIFF_AXIOMS_EXCEL_FILE_NAME)
    
def compare_ontological_resources(ontology_1: Graph, ontology_2: Graph, config: ComparisionConfig) -> list:
    diff_classes = compare_iris_in_type(ontology_1, ontology_2, OWL.Class, config)
    diff_object_properties = compare_iris_in_type(ontology_1, ontology_2, OWL.ObjectProperty, config)
    diff_datatype_properties = compare_iris_in_type(ontology_1, ontology_2, OWL.DatatypeProperty, config)
    diff_annotation_properties = compare_iris_in_type(ontology_1, ontology_2, OWL.DatatypeProperty, config)
    diff_individuals = compare_iris_in_type(ontology_1, ontology_2, OWL.NamedIndividual, config)
    diff_datatypes = compare_iris_in_type(ontology_1, ontology_2, RDFS.Datatype, config)
    diff_dict_list = [diff_classes, diff_object_properties, diff_datatype_properties, diff_annotation_properties, diff_individuals, diff_datatypes]
    non_empty_diff_dict_list = [diff_dict for diff_dict in diff_dict_list if len(diff_dict) > 0]
    
    return non_empty_diff_dict_list


def compare_axioms_for_same_subjects(ontology_1: Graph, ontology_2: Graph, config: ComparisionConfig) -> list:
    identifiable_subjects_1 = get_subjects(ontology_1, True)
    identifiable_subjects_2 = get_subjects(ontology_2, True)
    diffs = list()
    
    common_subjects = identifiable_subjects_1.intersection(identifiable_subjects_2)
    for common_identifiable_subject in common_subjects:
        diff = dict()
        
        property_object_tuples_1 = set(ontology_1.predicate_objects(subject=common_identifiable_subject))
        property_object_tuples_2 = set(ontology_2.predicate_objects(subject=common_identifiable_subject))
    
        identifiable_property_object_tuples_1 = identify_property_object_tuples(property_object_tuples_1, ontology_1)
        identifiable_property_object_tuples_2 = identify_property_object_tuples(property_object_tuples_2, ontology_2)
        identifiable_property_object_tuples_1_and_not_2 = list(identifiable_property_object_tuples_1.difference(identifiable_property_object_tuples_2))
        identifiable_property_object_tuples_2_and_not_1 = list(identifiable_property_object_tuples_2.difference(identifiable_property_object_tuples_1))
        
        if config.strict:
            if len(identifiable_property_object_tuples_1_and_not_2) == 0 and len(identifiable_property_object_tuples_2_and_not_1) == 0:
                continue
        
        if not config.verbose:
            diff = diff | \
                {
                    'subject': common_identifiable_subject,
                    KEY_1_MINUS_2_COUNT: len(identifiable_property_object_tuples_1_and_not_2),
                    KEY_2_MINUS_1_COUNT: len(identifiable_property_object_tuples_2_and_not_1)
                }
        else:
            diff = diff | \
                {
                    'subject': common_identifiable_subject,
                    KEY_1_MINUS_2: identifiable_property_object_tuples_1_and_not_2,
                    KEY_2_MINUS_1: identifiable_property_object_tuples_2_and_not_1,
                }
        
        if config.show_common:
            identifiable_property_object_tuples_1_and_2 = list(identifiable_property_object_tuples_1.intersection(identifiable_property_object_tuples_2))
            if not config.verbose:
                diff = diff | {KEY_1_AND_2_COUNT: len(identifiable_property_object_tuples_1_and_2)}
            else:
                diff = diff | {KEY_1_AND_2: identifiable_property_object_tuples_1_and_2}
        diffs.append(diff)
    
    return diffs


def compare_iris_in_type(ontology_1: Graph, ontology_2: Graph, ontology_type, config: ComparisionConfig) -> dict:
    resources_1 = set(ontology_1.subjects(predicate=RDF.type, object=ontology_type))
    resources_2 = set(ontology_2.subjects(predicate=RDF.type, object=ontology_type))
    iris_1 = filter_to_iris(resources_1)
    iris_2 = filter_to_iris(resources_2)
    
    diff_1_minus_2 = list(iris_1.difference(iris_2))
    diff_2_minus_1 = list(iris_2.difference(iris_1))
    common_1_and_2 = list(iris_1.intersection(iris_2))
    
    if config.strict:
        if len(diff_1_minus_2) == 0 and len(diff_2_minus_1) == 0:
            return dict()
    
    if not config.verbose:
        diff_dict = \
            {
                'type': str(ontology_type),
                KEY_1_MINUS_2_COUNT: len(diff_1_minus_2),
                KEY_2_MINUS_1_COUNT: len(diff_2_minus_1),
            }
    else:
        diff_dict = \
            {
                'type' : str(ontology_type),
                KEY_1_MINUS_2: diff_1_minus_2,
                KEY_2_MINUS_1: diff_2_minus_1
            }
    if config.show_common:
        if not config.verbose:
            diff_dict = diff_dict | {KEY_1_AND_2_COUNT: len(common_1_and_2)}
        else:
            common_1_and_2 = list(iris_1.intersection(iris_2))
            diff_dict = diff_dict | {KEY_1_AND_2: common_1_and_2}
    
    return diff_dict


def identify_property_object_tuples(property_object_tuples: set, ontology: Graph) -> set:
    identifiable_property_object_tuples = set()
    for property_object_tuple in property_object_tuples:
        property = property_object_tuple[0]
        triple_object = property_object_tuple[1]
        identifiable_triple_object = identify_resource(triple_object, ontology)
        identifiable_property_object_tuples.add(tuple([property, identifiable_triple_object]))
    return identifiable_property_object_tuples
  
  

def get_subjects(ontology: Graph, only_identifiable=False) -> set:
    subjects = set()
    for (subject, property, object) in ontology:
        if only_identifiable:
            if isinstance(subject, URIRef):
                subjects.add(subject)
        else:
            subjects.add(subject)
            
    return subjects

    
def filter_predicate_object_tuples_to_identifiable_objects(predicate_object_tuples: set) -> set:
    identifiable_predicate_object_tuples = set()
    for predicate_object_tuple in predicate_object_tuples:
        object = predicate_object_tuple[1]
        if isinstance(object,URIRef) or isinstance(object, Literal):
            identifiable_predicate_object_tuples.add(predicate_object_tuple)
    return identifiable_predicate_object_tuples
    
    
def filter_to_iris(resources) -> set:
    iris = set()
    for resource in resources:
        if isinstance(resource, URIRef):
            iris.add(resource)
    return iris

#
# # compare_ontologies('/Users/pawel.garbacz/Desktop/ontology-autonomous-driving.ttl', '/Users/pawel.garbacz/Desktop/VehicleAutomationLevels.ttl', 'test')
# compare_ontologies('resources/AboutIDMPDevMerged_v0.1.0.ttl', 'resources/AboutIDMPDevMerged_latest.ttl', 'test')
