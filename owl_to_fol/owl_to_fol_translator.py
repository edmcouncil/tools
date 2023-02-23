from rdflib import Graph, OWL, RDF, RDFS
from rdflib.term import Node

from owl_to_fol.objects.atomic_formula import AtomicFormula
from owl_to_fol.objects.identity_formula import IdentityFormula
from owl_to_fol.objects.negation import Negation
from owl_to_fol.objects.predicate import Predicate
from owl_to_fol.objects.symbol import Symbol
from owl_to_fol.objects.term import Term
from owl_to_fol.owl_to_fol_preparer import populate_default_predicates


def translate_owl_ontology_to_fol(owl_ontology:Graph):
    populate_default_predicates()
    for rdf_triple in owl_ontology:
        translate_rdf_triple_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
    v=0
      
        
def translate_rdf_triple_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    rdf_triple_subject = rdf_triple[0]
    rdf_triple_predicate = rdf_triple[1]
    rdf_triple_object = rdf_triple[2]
    
    rdf_triple_subject_is_out_of_scope = check_if_node_is_out_of_scope(node=rdf_triple_subject, owl_ontology=owl_ontology)
    if rdf_triple_subject_is_out_of_scope:
        return

    rdf_triple_predicate_is_out_of_scope = check_if_node_is_out_of_scope(node=rdf_triple_predicate, owl_ontology=owl_ontology)
    if rdf_triple_predicate_is_out_of_scope:
        return

    rdf_triple_object_is_out_of_scope = check_if_node_is_out_of_scope(node=rdf_triple_object, owl_ontology=owl_ontology)
    if rdf_triple_object_is_out_of_scope:
        return

    triple_subject = get_fol_object_for_node(node=rdf_triple_subject,owl_ontology=owl_ontology)
    triple_predicate = get_fol_object_for_node(node=rdf_triple_predicate, owl_ontology=owl_ontology, arity=2)
    triple_object = get_fol_object_for_node(node=rdf_triple_object, owl_ontology=owl_ontology)

    if isinstance(triple_subject, Term):
        translate_rdf_triple_with_individual_subject_to_fol(fol_triple=(triple_subject, triple_predicate, triple_object))
    
    if isinstance(triple_subject, Predicate):
        pass
        

def check_if_node_is_out_of_scope(node: Node, owl_ontology: Graph) -> bool:
    if (node, RDF.type, OWL.Ontology) in owl_ontology:
        return True

def get_fol_object_for_node(node: Node, owl_ontology: Graph, arity=1) -> Symbol:
    if (node, RDF.type, OWL.NamedIndividual) in owl_ontology:
        if node in Term.registry:
            return Term.registry[node]
        else:
            return Term(origin=node)
    
    if (node, RDF.type, RDFS.Literal) in owl_ontology:
        if node in Term.registry:
            return Term.registry[node]
        else:
            return Term(origin=node)
        
    else:
        return Predicate(origin=node, arity=arity)
    
    
def translate_rdf_triple_with_individual_subject_to_fol(fol_triple: tuple):
    if fol_triple[1].origin == RDF.type:
        AtomicFormula(predicate=fol_triple[2], arguments=[fol_triple[0]])
        return
    if fol_triple[1].origin == OWL.sameAs:
        IdentityFormula(predicate=fol_triple[1], arguments=[fol_triple[0], fol_triple[2]])
        return
    if fol_triple[1].origin == OWL.differentFrom:
        Negation(arguments=[IdentityFormula(predicate=fol_triple[1], arguments=[fol_triple[0], fol_triple[2]])])
        return
    AtomicFormula(predicate=fol_triple[1], arguments=[fol_triple[0], fol_triple[2]])
    
iof = Graph()
iof.parse('/Users/pawel.garbacz/Documents/edmc/github/edmc/tools/resources/iof/dev.iof-quickstart.ttl')
translate_owl_ontology_to_fol(owl_ontology=iof)