from rdflib import URIRef, RDF, Graph

from logic.fol_logic.objects.formula import Formula


def translate_rdf_construct_to_fol_subformula(rdf_predicate: URIRef, sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    match rdf_predicate:
        case RDF.type : return __translate_rdf_type(arguments=sw_arguments, variables=variables)


def __translate_rdf_type(arguments: list, variables: list) -> Formula:
    pass