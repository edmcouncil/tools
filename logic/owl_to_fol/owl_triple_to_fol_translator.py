from rdflib import Graph, OWL, RDF, RDFS
from rdflib.term import Node, BNode

from logic.owl_to_fol.objects.atomic_formula import AtomicFormula
from logic.owl_to_fol.objects.conjunction import Conjunction
from logic.owl_to_fol.objects.default_variable import DefaultVariable, TPTP_DEFAULT_LETTER_1, TPTP_DEFAULT_LETTER_2, \
    TPTP_DEFAULT_LETTER_3
from logic.owl_to_fol.objects.equivalence import Equivalence
from logic.owl_to_fol.objects.formula import Formula
from logic.owl_to_fol.objects.identity_formula import IdentityFormula
from logic.owl_to_fol.objects.implication import Implication
from logic.owl_to_fol.objects.negation import Negation
from logic.owl_to_fol.objects.predicate import Predicate
from logic.owl_to_fol.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.owl_to_fol.objects.symbol import Symbol
from logic.owl_to_fol.objects.term import Term
from logic.owl_to_fol.owl_helpers import uri_is_property
from logic.owl_to_fol.owl_node_to_fol_translator import get_simple_subformula_from_node, get_fol_object_for_node
from logic.owl_to_fol.owl_to_fol_preparer import populate_default_predicates


def translate_rdf_triple_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    rdf_triple_subject = rdf_triple[0]
    rdf_triple_predicate = rdf_triple[1]
    rdf_triple_object = rdf_triple[2]
    
    rdf_triple_subject_is_out_of_scope = node_is_out_of_scope(node=rdf_triple_subject, owl_ontology=owl_ontology)
    if rdf_triple_subject_is_out_of_scope:
        return
    
    rdf_triple_predicate_is_out_of_scope = node_is_out_of_scope(node=rdf_triple_predicate, owl_ontology=owl_ontology)
    if rdf_triple_predicate_is_out_of_scope:
        return
    
    rdf_triple_object_is_out_of_scope = node_is_out_of_scope(node=rdf_triple_object, owl_ontology=owl_ontology)
    if rdf_triple_object_is_out_of_scope:
        return
    
    rdf_triple_object_is_out_of_scope = triple_is_of_of_scope(rdf_triple=rdf_triple)
    if rdf_triple_object_is_out_of_scope:
        return
    
    rdf_triple = (rdf_triple_subject, rdf_triple_predicate, rdf_triple_object)
    
    if (rdf_triple_subject, RDF.type, OWL.NamedIndividual) in owl_ontology:
        translate_rdf_triple_about_individual_subject_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
        return
    
    if (rdf_triple_subject, RDF.type, OWL.Class) in owl_ontology:
        translate_rdf_triple_about_class_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
        return
        
    if uri_is_property(uri=rdf_triple_subject, owl_ontology=owl_ontology):
        translate_rdf_triple_about_property_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
        return
    
    v=0


def node_is_out_of_scope(node: Node, owl_ontology: Graph) -> bool:
    if (node, RDF.type, OWL.Ontology) in owl_ontology:
        return True
    if (node, RDF.type, OWL.AnnotationProperty) in owl_ontology:
        return True
    if len(set(owl_ontology.objects(subject=node, predicate=RDF.type))) == 0:
        return True
    return False

def triple_is_of_of_scope(rdf_triple: tuple) -> bool:
    if rdf_triple[0] in RDF:
        return True
    if rdf_triple[0] in RDFS:
        return True
    if rdf_triple[0] in OWL:
        return True
    
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.Class:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.Restriction:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.ObjectProperty:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.DatatypeProperty:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == RDF.Property:
        return True
    if rdf_triple[1] == OWL.imports:
        return True
    
    return False


def translate_rdf_triple_about_individual_subject_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    triple_subject = get_fol_object_for_node(node=rdf_triple[0], owl_ontology=owl_ontology)
    triple_predicate = get_fol_object_for_node(node=rdf_triple[1], owl_ontology=owl_ontology, arity=2)
    triple_object = get_fol_object_for_node(node=rdf_triple[2], owl_ontology=owl_ontology)
    if rdf_triple[1] == RDF.type:
        get_simple_subformula_from_node(node=rdf_triple[2], variable=rdf_triple[0], owl_ontology=owl_ontology)
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
        left_class = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        right_class = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology)
        if not left_class is None and not right_class is None:
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[left_class, right_class]),
                variables=[DefaultVariable()],
                quantifier=Quantifier.UNIVERSAL)
        return
    if rdf_triple[1] == OWL.equivalentClass:
        left_class = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        right_class = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology)
        if not left_class is None and not right_class is None:
            QuantifyingFormula(
                quantified_formula=Equivalence(arguments=[left_class, right_class]),
                variables=[DefaultVariable()],
                quantifier=Quantifier.UNIVERSAL)
        return
    
    if rdf_triple[1] == OWL.complementOf:
        left_class = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        right_class = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology)
        if not left_class is None and not right_class is None:
            QuantifyingFormula(
                quantified_formula=Equivalence(arguments=[left_class, Negation(arguments=[right_class])]),
                variables=[DefaultVariable()],
                quantifier=Quantifier.UNIVERSAL)
        return
    
    if rdf_triple[1] == OWL.disjointWith:
        left_class = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        right_class = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology)
        if not left_class is None and not right_class is None:
            overlap_formula = \
                QuantifyingFormula(
                    quantified_formula=Conjunction(arguments=[left_class, right_class]),
                    variables=[DefaultVariable()],
                    quantifier=Quantifier.EXISTENTIAL)
            formula = Negation(arguments=[overlap_formula])
            return formula
        
    v=0

    
def translate_rdf_triple_about_property_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    if rdf_triple[1] == RDFS.subPropertyOf:
        antecedent = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        subsequent = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology)
        if not antecedent is None and not subsequent is None:
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[antecedent, subsequent]),
                variables=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)],
                quantifier=Quantifier.UNIVERSAL)
        return
    
    if rdf_triple[1] == OWL.equivalentProperty:
        antecedent = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        subsequent = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology)
        if not antecedent is None and not subsequent is None:
            QuantifyingFormula(
                quantified_formula=Equivalence(arguments=[antecedent, subsequent]),
                variables=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)],
                quantifier=Quantifier.UNIVERSAL)
        return
    
    if rdf_triple[1] == RDFS.domain:
        antecedent = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        subsequent = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology)
        if not antecedent is None and not subsequent is None:
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[antecedent, subsequent]),
                variables=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)],
                quantifier=Quantifier.UNIVERSAL)
        return
    
    if rdf_triple[1] == RDFS.range:
        antecedent = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        subsequent = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology, variable=DefaultVariable(letter=TPTP_DEFAULT_LETTER_2))
        if not antecedent is None and not subsequent is None:
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[antecedent, subsequent]),
                variables=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)],
                quantifier=Quantifier.UNIVERSAL)
        return
    
    if rdf_triple[1] == OWL.inverseOf:
        antecedent = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
        subsequent = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology,variable=DefaultVariable(letter=TPTP_DEFAULT_LETTER_2))
        if not antecedent is None and not subsequent is None:
            subsequent.swap_arguments()
            QuantifyingFormula(
                quantified_formula=Equivalence(arguments=[antecedent, subsequent]),
                variables=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)],
                quantifier=Quantifier.UNIVERSAL)
        return
    
    if rdf_triple[1] == RDF.type:
        if rdf_triple[2] == OWL.TransitiveProperty:
            property_formula_1 = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
            property_formula_2 = property_formula_1.replace_arguments(arguments=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_2), DefaultVariable(letter=TPTP_DEFAULT_LETTER_3)])
            property_formula_3 = property_formula_1.replace_arguments(arguments=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_1),DefaultVariable(letter=TPTP_DEFAULT_LETTER_3)])
            quantifying_variables = [DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_2), DefaultVariable(letter=TPTP_DEFAULT_LETTER_3)]
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[Conjunction(arguments=[property_formula_1, property_formula_2]), property_formula_3]),
                variables=quantifying_variables,
                quantifier=Quantifier.UNIVERSAL)
            return
        if rdf_triple[2] == OWL.FunctionalProperty:
            property_formula_1 = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
            property_formula_2 = property_formula_1.replace_arguments(arguments=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_3)])
            identity_formula = IdentityFormula(arguments=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_2), DefaultVariable(letter=TPTP_DEFAULT_LETTER_3)])
            quantifying_variables = [DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_2), DefaultVariable(letter=TPTP_DEFAULT_LETTER_3)]
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[Conjunction(arguments=[property_formula_1, property_formula_2]), identity_formula]),
                variables=quantifying_variables,
                quantifier=Quantifier.UNIVERSAL)
            return
        if rdf_triple[2] == OWL.InverseFunctionalProperty:
            property_formula_1 = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology)
            property_formula_2 = property_formula_1.replace_arguments(arguments=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_3), DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)])
            identity_formula = IdentityFormula(arguments=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_3)])
            quantifying_variables = [DefaultVariable(letter=TPTP_DEFAULT_LETTER_1), DefaultVariable(letter=TPTP_DEFAULT_LETTER_2), DefaultVariable(letter=TPTP_DEFAULT_LETTER_3)]
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[Conjunction(arguments=[property_formula_1, property_formula_2]), identity_formula]),
                variables=quantifying_variables,
                quantifier=Quantifier.UNIVERSAL)
            return
        
    v=0