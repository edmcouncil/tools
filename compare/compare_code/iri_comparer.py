from rdflib import Graph, RDF, URIRef

from compare.compare_code.common import get_specific_constant, RESOURCES_LEFT_BUT_NOT_RIGHT, \
    RESOURCES_RIGHT_BUT_NOT_LEFT, BOTH
from compare.compare_code.comparison_config import ComparisonConfig


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


def filter_to_iris(resources) -> set:
    iris = set()
    for resource in resources:
        if isinstance(resource, URIRef):
            iris.add(resource)
    return iris
