from rdflib import Graph, OWL, RDF, RDFS
from rdflib.term import URIRef, Literal

from compare.common import ONTOLOGY_NAME_KEY, ONTOLOGY_DIFF_KEY, LEFT_BUT_NOT_RIGHT, RIGHT_BUT_NOT_LEFT, BOTH, \
    LEFT_BUT_NOT_RIGHT_COUNT, RIGHT_BUT_NOT_LEFT_COUNT, BOTH_COUNT
from compare.comparision_config import ComparisionConfig
from owl_helpers.resource_identifiers import identify_resource


def compare_ontology_revisions(
        ontology_revision_left_location: str,
        ontology_revision_right_location: str,
        ontology_name: str,
        config: ComparisionConfig) -> tuple:
    ontology_1 = Graph()
    if len(ontology_revision_left_location) > 0:
        ontology_1.parse(ontology_revision_left_location)
    ontology_2 = Graph()
    if len(ontology_revision_right_location) > 0:
        ontology_2.parse(ontology_revision_right_location)
    
    diff_resources = compare_ontological_resources(ontology_name, ontology_1, ontology_2, config)
    diff_axioms_for_same_subjects = compare_axioms_for_same_subjects(ontology_name, ontology_1, ontology_2, config)
    return diff_resources, diff_axioms_for_same_subjects


def compare_ontological_resources(ontology_name: str, ontology_1: Graph, ontology_2: Graph, config: ComparisionConfig) -> dict:
    diff_classes = compare_iris_in_type(ontology_1, ontology_2, OWL.Class, config)
    diff_object_properties = compare_iris_in_type(ontology_1, ontology_2, OWL.ObjectProperty, config)
    diff_datatype_properties = compare_iris_in_type(ontology_1, ontology_2, OWL.DatatypeProperty, config)
    diff_annotation_properties = compare_iris_in_type(ontology_1, ontology_2, OWL.DatatypeProperty, config)
    diff_individuals = compare_iris_in_type(ontology_1, ontology_2, OWL.NamedIndividual, config)
    diff_datatypes = compare_iris_in_type(ontology_1, ontology_2, RDFS.Datatype, config)
    
    diff_dict_list = \
        [
            diff_classes,
            diff_object_properties,
            diff_datatype_properties,
            diff_annotation_properties,
            diff_individuals,
            diff_datatypes]
    
    non_empty_diff_dict_list = [diff_dict for diff_dict in diff_dict_list if len(diff_dict) > 0]
    if config.strict:
        if len(non_empty_diff_dict_list) > 0:
            diffs_dict = {ONTOLOGY_NAME_KEY: ontology_name, ONTOLOGY_DIFF_KEY: non_empty_diff_dict_list}
        else:
            diffs_dict = dict()
    else:
        diffs_dict = {ONTOLOGY_NAME_KEY: ontology_name, ONTOLOGY_DIFF_KEY: non_empty_diff_dict_list}
    return diffs_dict


def compare_axioms_for_same_subjects(ontology_name: str, ontology_1: Graph, ontology_2: Graph, config: ComparisionConfig) -> dict:
    identifiable_subjects_1 = get_subjects(ontology_1, True)
    identifiable_subjects_2 = get_subjects(ontology_2, True)
    diffs_dict_list = list()
    
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
                       LEFT_BUT_NOT_RIGHT_COUNT: len(identifiable_property_object_tuples_1_and_not_2),
                       RIGHT_BUT_NOT_LEFT_COUNT: len(identifiable_property_object_tuples_2_and_not_1)
                   }
        else:
            diff = diff | \
                   {
                       'subject': common_identifiable_subject,
                       LEFT_BUT_NOT_RIGHT: identifiable_property_object_tuples_1_and_not_2,
                       RIGHT_BUT_NOT_LEFT: identifiable_property_object_tuples_2_and_not_1,
                   }
        
        if config.show_common:
            identifiable_property_object_tuples_1_and_2 = list(
                identifiable_property_object_tuples_1.intersection(identifiable_property_object_tuples_2))
            if not config.verbose:
                diff = diff | {BOTH_COUNT: len(identifiable_property_object_tuples_1_and_2)}
            else:
                diff = diff | {BOTH: identifiable_property_object_tuples_1_and_2}
        diffs_dict_list.append(diff)
    
    if config.strict:
        if len(diffs_dict_list) > 0:
            diffs_dict = {ONTOLOGY_NAME_KEY: ontology_name, ONTOLOGY_DIFF_KEY: diffs_dict_list}
        else:
            diffs_dict = dict()
    else:
        diffs_dict = {ONTOLOGY_NAME_KEY: ontology_name, ONTOLOGY_DIFF_KEY: diffs_dict_list}
    
    return diffs_dict


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
                LEFT_BUT_NOT_RIGHT_COUNT: len(diff_1_minus_2),
                RIGHT_BUT_NOT_LEFT_COUNT: len(diff_2_minus_1),
            }
    else:
        diff_dict = \
            {
                'type': str(ontology_type),
                LEFT_BUT_NOT_RIGHT: diff_1_minus_2,
                RIGHT_BUT_NOT_LEFT: diff_2_minus_1
            }
    if config.show_common:
        if not config.verbose:
            diff_dict = diff_dict | {BOTH_COUNT: len(common_1_and_2)}
        else:
            common_1_and_2 = list(iris_1.intersection(iris_2))
            diff_dict = diff_dict | {BOTH: common_1_and_2}
    
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
        if isinstance(object, URIRef) or isinstance(object, Literal):
            identifiable_predicate_object_tuples.add(predicate_object_tuple)
    return identifiable_predicate_object_tuples


def filter_to_iris(resources) -> set:
    iris = set()
    for resource in resources:
        if isinstance(resource, URIRef):
            iris.add(resource)
    return iris
