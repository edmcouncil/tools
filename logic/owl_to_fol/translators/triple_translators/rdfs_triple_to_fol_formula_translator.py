from rdflib import URIRef, RDFS, Graph

from logic.fol_logic.objects.formula import Formula


def translate_rdfs_construct_to_fol_formula(rdfs_predicate: URIRef, sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    match rdfs_predicate:
        case RDFS.subClassOf : return __translate_rdfs_subclassof(fol_arguments=sw_arguments, variables=variables)


def __translate_rdfs_subclassof(fol_arguments: list, variables: list) -> Formula:
    pass