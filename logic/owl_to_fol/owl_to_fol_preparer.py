import logging

from rdflib import RDF, RDFS, OWL, Graph

from logic.fol_logic.objects.predicate import Predicate


def populate_default_predicates():
    logging.info(msg='Populating W3C predicates')
    populate_default_predicates_from_namespace(namespace=RDF, context='rdf')
    populate_default_predicates_from_namespace(namespace=RDFS, context='rdfs')
    populate_default_predicates_from_namespace(namespace=OWL, context='owl')
    
    
def populate_default_predicates_from_namespace(namespace: type, context: str):
    resources = namespace.as_jsonld_context(context)
    resources_in_context = resources['@context']
    for resource_in_context in resources_in_context.values():
        if not resource_in_context == context:
            if resource_in_context[len(context)+1].islower():
                Predicate(origin_value=resource_in_context, arity=2)
            else:
                Predicate(origin_value=resource_in_context, arity=1)
                
                
def import_default_sw_ontologies(rdf_graph: Graph):
    logging.info(msg='Importing W3C default ontologies')
    rdf_graph += rdf_graph.parse(str(RDF))
    rdf_graph += rdf_graph.parse(str(RDFS))
    rdf_graph += rdf_graph.parse(str(OWL))
                