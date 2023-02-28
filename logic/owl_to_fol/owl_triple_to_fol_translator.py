from rdflib import Graph, OWL, RDF, RDFS
from rdflib.term import Node, BNode

from logic.owl_to_fol.objects.atomic_formula import AtomicFormula
from logic.owl_to_fol.objects.default_variable import DefaultVariable
from logic.owl_to_fol.objects.formula import Formula
from logic.owl_to_fol.objects.identity_formula import IdentityFormula
from logic.owl_to_fol.objects.implication import Implication
from logic.owl_to_fol.objects.negation import Negation
from logic.owl_to_fol.objects.predicate import Predicate
from logic.owl_to_fol.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.owl_to_fol.objects.symbol import Symbol
from logic.owl_to_fol.objects.term import Term
from logic.owl_to_fol.owl_node_to_fol_translator import get_subformula_from_node, get_fol_object_for_node
from logic.owl_to_fol.owl_to_fol_preparer import populate_default_predicates


def translate_rdf_triple_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    rdf_triple_subject = rdf_triple[0]
    rdf_triple_predicate = rdf_triple[1]
    rdf_triple_object = rdf_triple[2]
    
    rdf_triple_subject_is_out_of_scope = check_if_node_is_out_of_scope(node=rdf_triple_subject,owl_ontology=owl_ontology)
    if rdf_triple_subject_is_out_of_scope:
        return
    
    rdf_triple_predicate_is_out_of_scope = check_if_node_is_out_of_scope(node=rdf_triple_predicate,owl_ontology=owl_ontology)
    if rdf_triple_predicate_is_out_of_scope:
        return
    
    rdf_triple_object_is_out_of_scope = check_if_node_is_out_of_scope(node=rdf_triple_object, owl_ontology=owl_ontology)
    if rdf_triple_object_is_out_of_scope:
        return
    
    rdf_triple = (rdf_triple_subject, rdf_triple_predicate, rdf_triple_object)
    if (rdf_triple_subject, RDF.type, OWL.NamedIndividual) in owl_ontology:
        translate_rdf_triple_about_individual_subject_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
    
    if (rdf_triple_subject, RDF.type, OWL.Class) in owl_ontology:
        translate_rdf_triple_about_class_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)


def check_if_node_is_out_of_scope(node: Node, owl_ontology: Graph) -> bool:
    if (node, RDF.type, OWL.Ontology) in owl_ontology:
        return True
    if (node, RDF.type, OWL.AnnotationProperty) in owl_ontology:
        return True
    if len(set(owl_ontology.objects(subject=node, predicate=RDF.type))) == 0:
        return True
    return False


def translate_rdf_triple_about_individual_subject_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    triple_subject = get_fol_object_for_node(node=rdf_triple[0], owl_ontology=owl_ontology)
    triple_predicate = get_fol_object_for_node(node=rdf_triple[1], owl_ontology=owl_ontology, arity=2)
    triple_object = get_fol_object_for_node(node=rdf_triple[2], owl_ontology=owl_ontology)
    if rdf_triple[1] == RDF.type:
        get_subformula_from_node(node=rdf_triple[2], variable=rdf_triple[0], owl_ontology=owl_ontology)
        return
    if rdf_triple[1] == OWL.sameAs:
        IdentityFormula(arguments=[triple_subject, triple_object])
        return
    if rdf_triple[1] == OWL.differentFrom:
        Negation(arguments=[IdentityFormula(arguments=[triple_subject, triple_object])])
        return
    AtomicFormula(predicate=triple_predicate, arguments=[triple_subject, triple_object])


def translate_rdf_triple_about_class_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    if rdf_triple[1] == RDFS.subClassOf:
        antecedent = get_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        subsequent = get_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology)
        if not antecedent is None and not subsequent is None:
            QuantifyingFormula(quantified_formula=Implication(arguments=[antecedent, subsequent]),variables=[DefaultVariable()], quantifier=Quantifier.UNIVERSAL)
        return



