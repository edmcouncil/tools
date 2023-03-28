from rdflib import Graph, OWL, RDFS

from compare.compare_code.axiom_comparer import compare_axioms_for_same_subjects
from compare.compare_code.common import *
from compare.compare_code.comparison_config import ComparisonConfig
from compare.compare_code.iri_comparer import compare_iris_in_type


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

