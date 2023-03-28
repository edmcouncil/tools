from rdflib import Graph
from rdflib.term import URIRef

from compare.compare_code.common import *
from compare.compare_code.comparison_config import ComparisonConfig
from compare.compare_code.owl_helpers.resource_identifiers import identify_resource


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


def identify_property_object_tuples(property_object_tuples: set, ontology: Graph) -> set:
    identifiable_property_object_tuples = set()
    for property_object_tuple in property_object_tuples:
        tuple_property = property_object_tuple[0]
        tuple_object = property_object_tuple[1]
        identifiable_triple_object = identify_resource(tuple_object, ontology)
        if isinstance(identifiable_triple_object, list):
            identifiable_property_object_tuples.add(tuple([tuple_property] + identifiable_triple_object))
        else:
            identifiable_property_object_tuples.add(tuple([tuple_property, identifiable_triple_object]))
    return identifiable_property_object_tuples


def get_subjects(ontology: Graph, only_identifiable=False) -> set:
    subjects = set()
    for (triple_subject, triple_predicate, triple_object) in ontology:
        if only_identifiable:
            if isinstance(triple_subject, URIRef):
                subjects.add(triple_subject)
        else:
            subjects.add(triple_subject)
    
    return subjects

