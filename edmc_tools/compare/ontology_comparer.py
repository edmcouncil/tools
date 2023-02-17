from rdflib import Graph, OWL, RDF, RDFS
from rdflib.term import URIRef, Literal

from compare.code.common import *
from compare.code.comparison_config import ComparisonConfig
from owl_helpers.resource_identifiers import identify_resource


def compare_ontology_revisions(
        ontology_revision_left_location: str,
        ontology_revision_right_location: str,
        ontology_name: str,
        left_revision_id: str,
        right_revision_id: str,
        config: ComparisonConfig) -> tuple:
    ontology_1 = Graph()
    if len(ontology_revision_left_location) > 0:
        ontology_1.parse(ontology_revision_left_location)
    ontology_2 = Graph()
    if len(ontology_revision_right_location) > 0:
        ontology_2.parse(ontology_revision_right_location)
    
    diff_resources = compare_ontological_resources(ontology_name, ontology_1, ontology_2, config, left_revision_id, right_revision_id)
    diff_axioms_for_same_subjects = compare_axioms_for_same_subjects(ontology_name, ontology_1, ontology_2, config, left_revision_id, right_revision_id)
    return diff_resources, diff_axioms_for_same_subjects


def compare_ontological_resources(
        ontology_name: str,
        left_ontology: Graph,
        right_ontology: Graph,
        config: ComparisonConfig,
        left_revision_id: str,
        right_revision_id: str) -> dict:
    diff_classes = compare_iris_in_type(left_ontology, right_ontology, OWL.Class, config, left_revision_id, right_revision_id)
    diff_object_properties = compare_iris_in_type(left_ontology, right_ontology, OWL.ObjectProperty, config, left_revision_id, right_revision_id)
    diff_datatype_properties = compare_iris_in_type(left_ontology, right_ontology, OWL.DatatypeProperty, config, left_revision_id, right_revision_id)
    diff_annotation_properties = compare_iris_in_type(left_ontology, right_ontology, OWL.DatatypeProperty, config, left_revision_id, right_revision_id)
    diff_individuals = compare_iris_in_type(left_ontology, right_ontology, OWL.NamedIndividual, config, left_revision_id, right_revision_id)
    diff_datatypes = compare_iris_in_type(left_ontology, right_ontology, RDFS.Datatype, config, left_revision_id, right_revision_id)
    
    diff_dict_list = \
        [
            diff_classes,
            diff_object_properties,
            diff_datatype_properties,
            diff_annotation_properties,
            diff_individuals,
            diff_datatypes
        ]
    
    non_empty_diff_dict_list = [diff_dict for diff_dict in diff_dict_list if len(diff_dict) > 0]
    if config.strict:
        if len(non_empty_diff_dict_list) > 0:
            diffs_dict = {ONTOLOGY_NAME_KEY: ontology_name, ONTOLOGY_DIFF_KEY: non_empty_diff_dict_list}
        else:
            diffs_dict = dict()
    else:
        diffs_dict = {ONTOLOGY_NAME_KEY: ontology_name, ONTOLOGY_DIFF_KEY: non_empty_diff_dict_list}
    return diffs_dict


def compare_axioms_for_same_subjects(
        ontology_name: str,
        ontology_1: Graph,
        ontology_2: Graph,
        config: ComparisonConfig,
        left_revision_id: str,
        right_revision_id: str,) -> dict:
    identifiable_subjects_1 = get_subjects(ontology_1, True)
    identifiable_subjects_2 = get_subjects(ontology_2, True)
    diffs_dict_list = list()

    left_but_not_right = \
        get_specific_constant(
            constant=AXIOMS_LEFT_BUT_NOT_RIGHT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    right_but_not_left = \
        get_specific_constant(
            constant=AXIOMS_RIGHT_BUT_NOT_LEFT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    
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
                       left_but_not_right: len(identifiable_property_object_tuples_1_and_not_2),
                       right_but_not_left.replace('right', right_revision_id): len(identifiable_property_object_tuples_2_and_not_1)
                   }
        else:
            diff = diff | \
                   {
                       'subject': common_identifiable_subject,
                       left_but_not_right: identifiable_property_object_tuples_1_and_not_2,
                       right_but_not_left.replace('right', right_revision_id): identifiable_property_object_tuples_2_and_not_1,
                   }
        
        if config.show_common:
            identifiable_property_object_tuples_1_and_2 = list(
                identifiable_property_object_tuples_1.intersection(identifiable_property_object_tuples_2))
            if not config.verbose:
                diff = diff | {BOTH: len(identifiable_property_object_tuples_1_and_2)}
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


def compare_iris_in_type(
        left_ontology: Graph,
        right_ontology: Graph,
        ontology_type, config: ComparisonConfig,
        left_revision_id: str,
        right_revision_id: str) -> dict:
    left_resources = set(left_ontology.subjects(predicate=RDF.type, object=ontology_type))
    right_resources = set(right_ontology.subjects(predicate=RDF.type, object=ontology_type))
    left_iris = filter_to_iris(left_resources)
    right_iris = filter_to_iris(right_resources)
    
    diff_left_minus_right = list(left_iris.difference(right_iris))
    diff_right_minus_left = list(right_iris.difference(left_iris))
    
    common = list(left_iris.intersection(right_iris))

    left_but_not_right_key_name = \
        get_specific_constant(
            constant=RESOURCES_LEFT_BUT_NOT_RIGHT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    right_but_not_left_key_name = \
        get_specific_constant(
            constant=RESOURCES_RIGHT_BUT_NOT_LEFT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    
    if config.strict:
        if len(diff_left_minus_right) == 0 and len(diff_right_minus_left) == 0:
            return dict()
    
    if not config.verbose:
        diff_dict = \
            {
                'type': str(ontology_type),
                left_but_not_right_key_name: len(diff_left_minus_right),
                right_but_not_left_key_name: len(diff_right_minus_left),
            }
    else:
        diff_dict = \
            {
                'type': str(ontology_type),
                left_but_not_right_key_name: diff_left_minus_right,
                right_but_not_left_key_name: diff_right_minus_left
            }
    if config.show_common:
        if not config.verbose:
            diff_dict = diff_dict | {BOTH: len(common)}
        else:
            common = list(left_iris.intersection(right_iris))
            diff_dict = diff_dict | {BOTH: common}
    
    return diff_dict


def identify_property_object_tuples(property_object_tuples: set, ontology: Graph) -> set:
    identifiable_property_object_tuples = set()
    for property_object_tuple in property_object_tuples:
        tuple_property = property_object_tuple[0]
        tuple_object = property_object_tuple[1]
        identifiable_triple_object = identify_resource(tuple_object, ontology)
        identifiable_property_object_tuples.add(tuple([tuple_property, identifiable_triple_object]))
    return identifiable_property_object_tuples


def get_subjects(ontology: Graph, only_identifiable=False) -> set:
    subjects = set()
    for (subject, relation, object) in ontology:
        if only_identifiable:
            if isinstance(subject, URIRef):
                subjects.add(subject)
        else:
            subjects.add(subject)
    
    return subjects


def filter_predicate_object_tuples_to_identifiable_objects(predicate_object_tuples: set) -> set:
    identifiable_predicate_object_tuples = set()
    for predicate_object_tuple in predicate_object_tuples:
        tuple_object = predicate_object_tuple[1]
        if isinstance(tuple_object, URIRef) or isinstance(tuple_object, Literal):
            identifiable_predicate_object_tuples.add(predicate_object_tuple)
    return identifiable_predicate_object_tuples


def filter_to_iris(resources) -> set:
    iris = set()
    for resource in resources:
        if isinstance(resource, URIRef):
            iris.add(resource)
    return iris
