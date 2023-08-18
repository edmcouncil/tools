import logging
from collections import OrderedDict

from rdflib import XSD, Graph




def prepare_datatypes_dictionary(datatypes_attributes_map: dict, ontology: Graph) -> dict:
    logging.info(msg='Preparing datatypes')
    datatypes_dictionary = dict()
    for restricted_class, restrictions in datatypes_attributes_map.items():
        if len(restrictions) == 0:
            continue
        prefixed_restricted_class = restricted_class.n3(ontology.namespace_manager)
        datatypes = set()
        for restriction in restrictions:
            restricting_property = restriction[0]
            restricting_class = restriction[1]
            prefixed_restricting_property = restricting_property.n3(ontology.namespace_manager)
            prefixed_restricting_class = restricting_class.n3(ontology.namespace_manager)
            datatypes.add((prefixed_restricting_property, prefixed_restricting_class))
        datatypes_dictionary[prefixed_restricted_class] = datatypes
    return datatypes_dictionary


def order_datatypes(datatypes_dictionary: dict, ordered_datatypes: dict, attribute_rank: int):
    attribute_rank += 1
    if attribute_rank in ordered_datatypes:
        datatypes_at_rank = ordered_datatypes[attribute_rank]
    else:
        datatypes_at_rank = set()
        ordered_datatypes[attribute_rank] = datatypes_at_rank
    datatypes_dictionary_copy = datatypes_dictionary.copy()
    dependent_datatypes = __collect_all_dependent_datatypes(datatypes_attributes_map=datatypes_dictionary)
    for datatype, datatype_attributes in datatypes_dictionary.items():
        datatype_attributes_copy = datatype_attributes.copy()
        for [attribute, attribute_datatype] in set(datatype_attributes):
            if attribute_datatype not in dependent_datatypes:
                datatype_attributes_copy.remove((attribute, attribute_datatype))
                datatypes_at_rank.add(attribute_datatype)
        datatypes_dictionary_copy[datatype] = datatype_attributes_copy
        if len(datatypes_dictionary_copy[datatype]) == 0:
            datatypes_dictionary_copy.pop(datatype)
            if attribute_rank+1 in ordered_datatypes:
                datatypes_at_rank_plus = ordered_datatypes[attribute_rank+1]
            else:
                datatypes_at_rank_plus = set()
                ordered_datatypes[attribute_rank + 1] = datatypes_at_rank_plus
            datatypes_at_rank_plus.add(datatype)
    if len(datatypes_dictionary_copy) > 0:
        ordered_datatypes = order_datatypes(datatypes_dictionary=datatypes_dictionary_copy, ordered_datatypes=ordered_datatypes, attribute_rank=attribute_rank)
    return ordered_datatypes
        

def __collect_all_dependent_datatypes(datatypes_attributes_map: dict) -> set:
    dependent_datatypes = set()
    for datatype in datatypes_attributes_map.keys():
        dependent_datatypes.add(datatype)
    return dependent_datatypes


def __get_datatypes_from_map(datatypes_attributes_map: dict):
    datatypes = set()
    for datatype, datatype_attributes in datatypes_attributes_map.items():
        datatypes.add(datatype)
        for attribute, attribute_datatype in datatype_attributes:
            datatypes.add(attribute_datatype)
    return datatypes


def __get_datatypes_dependencies(datatypes_attributes_map: dict) -> dict:
    datatypes_dependencies_map = dict()
    for datatype, datatype_attributes in datatypes_attributes_map.items():
        __get_datatype_dependencies(datatype=datatype,datatypes_dependencies_map=datatypes_dependencies_map,datatypes_attributes_map=datatypes_attributes_map)
    return datatypes_dependencies_map
    
    
def __get_datatype_dependencies(datatype, datatypes_dependencies_map: dict, datatypes_attributes_map: dict):
    for [attribute, attribute_datatype] in datatypes_attributes_map[datatype]:
        if datatype in datatypes_dependencies_map:
            attribute_datatype_dependencies = datatypes_dependencies_map[datatype]
        else:
            attribute_datatype_dependencies = set()
            datatypes_dependencies_map[datatype] = attribute_datatype_dependencies
        attribute_datatype_dependencies.add(attribute_datatype)
        if attribute_datatype in datatypes_attributes_map:
            __get_datatype_dependencies(datatype=attribute_datatype, datatypes_dependencies_map=datatypes_dependencies_map,datatypes_attributes_map=datatypes_attributes_map)
        