from rdflib import Graph, RDF, OWL

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.negation import Negation
from logic.owl_to_fol.translators.owl_node_to_fol_translator import get_simple_subformula_from_node
from logic.owl_to_fol.translators.translator_helpers import get_fol_symbol_for_owl_node


def translate_rdf_triple_about_individual_subject_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    triple_subject = get_fol_symbol_for_owl_node(node=rdf_triple[0], owl_ontology=owl_ontology)
    triple_predicate = get_fol_symbol_for_owl_node(node=rdf_triple[1], owl_ontology=owl_ontology, arity=2)
    triple_object = get_fol_symbol_for_owl_node(node=rdf_triple[2], owl_ontology=owl_ontology)
    if rdf_triple[1] == RDF.type:
        get_simple_subformula_from_node(node=rdf_triple[2], variables=[triple_subject], owl_ontology=owl_ontology)
        return
    if rdf_triple[1] == OWL.sameAs:
        IdentityFormula(arguments=[triple_subject, triple_object])
        return
    if rdf_triple[1] == OWL.differentFrom:
        Negation(arguments=[IdentityFormula(arguments=[triple_subject, triple_object])])
        return
    
    AtomicFormula(predicate=triple_predicate, arguments=[triple_subject, triple_object], is_self_standing=True)
