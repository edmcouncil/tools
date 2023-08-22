import logging

from rdflib import Graph, OWL, URIRef

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.disjunction import Disjunction
from logic.fol_logic.objects.equivalence import Equivalence
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.filterers.translation_filterer import node_is_out_of_scope, triple_is_of_of_scope
from logic.owl_to_fol.translators.owl_node_to_fol_translator import get_subformula_from_node


def translate_rdf_triple_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    Variable.clear_used_variable_letters()
    
    rdf_triple_subject = rdf_triple[0]
    rdf_triple_predicate = rdf_triple[1]
    rdf_triple_object = rdf_triple[2]
    
    rdf_triple_subject_is_out_of_scope = node_is_out_of_scope(node=rdf_triple_subject, owl_ontology=owl_ontology)
    if rdf_triple_subject_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(rdf_triple_subject) + ' as the subject')
        return
    
    rdf_triple_predicate_is_out_of_scope = node_is_out_of_scope(node=rdf_triple_predicate, owl_ontology=owl_ontology)
    if rdf_triple_predicate_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(rdf_triple_predicate) + ' as the predicate')
        return
    
    rdf_triple_object_is_out_of_scope = node_is_out_of_scope(node=rdf_triple_object, owl_ontology=owl_ontology)
    if rdf_triple_object_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(rdf_triple_object) + ' as the object')
        return
    
    rdf_triple_is_out_of_scope = triple_is_of_of_scope(rdf_triple=rdf_triple)
    if rdf_triple_is_out_of_scope:
        logging.info('Dropping an out-of scope triple ' + str(rdf_triple))
        return
    
    variables=[Variable(letter=Variable.get_next_variable_letter()), Variable(letter=Variable.get_next_variable_letter())]
    
    subject_fol_formula = get_subformula_from_node(node=rdf_triple_subject, owl_ontology=owl_ontology, variables=variables)
    if not subject_fol_formula:
        logging.warning(msg='Processing ' + str(rdf_triple) + 'as a triple subject returned None')
        return
    if isinstance(subject_fol_formula, list):
        logging.warning(msg='Processing ' + str(rdf_triple) + 'as a triple subject returned list')
        return
    object_fol_formula = get_subformula_from_node(node=rdf_triple_object, owl_ontology=owl_ontology, variables=variables)
    if not object_fol_formula:
        logging.warning(msg='Processing ' + str(rdf_triple) + 'as a triple subject returned None')
        return
    
    if rdf_triple_predicate in OWL:
        translate_owl_construct_to_self_standing_fol_formula(
            owl_type=rdf_triple_predicate,
            arguments=[subject_fol_formula, object_fol_formula],
            variables=variables)
    
    
def translate_owl_construct_to_self_standing_fol_formula(owl_type: URIRef, arguments: list, variables: list):
    match owl_type:
        case OWL.inverseOf:
            __translate_owl_inverse_of(arguments=arguments, variables=variables)
        case OWL.equivalentClass:
            __translate_owl_equivalent(arguments=arguments, variables=variables)
        case OWL.disjointUnionOf:
            __translate_owl_disjointunionof(arguments=arguments, variables=variables)


def __translate_owl_inverse_of(arguments: list, variables: list):
    if not len(arguments) == 2:
        logging.exception(msg='Wrong number of owl:inverseOf arguments')
        return None
    argument1 = arguments[0]
    argument2 = arguments[1]
    if not isinstance(argument1, AtomicFormula):
        logging.exception(msg='Wrong type of first argument of owl:inverseOf')
        return None
    if not isinstance(argument2, AtomicFormula):
        logging.exception(msg='Wrong type of second argument of owl:inverseOf')
        return None
    inverse_argument2 = argument2.swap_arguments()
    inverse_formula = \
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[argument1, inverse_argument2]),
            variables=variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return inverse_formula


def __translate_owl_equivalent(arguments: list, variables: list):
    if not len(arguments) == 2:
        logging.exception(msg='Wrong number of owl:inverseOf arguments')
        return None
    argument1 = arguments[0]
    argument2 = arguments[1]
    QuantifyingFormula(
        quantified_formula=Equivalence(arguments=[argument1, argument2]),
        variables=variables[:1],
        quantifier=Quantifier.UNIVERSAL,
        is_self_standing=True)


def __translate_owl_disjointunionof(arguments: list, variables: list):
    union_class_formula = arguments.pop(0)
    union_disjunction = Disjunction(arguments=arguments[0])
    
    QuantifyingFormula(
        quantified_formula=Equivalence(arguments=[union_class_formula, union_disjunction]),
        quantifier=Quantifier.UNIVERSAL,
        variables=variables[:1],
        is_self_standing=True)
    
    for index1 in range(len(arguments) - 1):
        argument1 = arguments[index1]
        for index2 in range(index1 + 1, len(arguments)):
            argument2 = arguments[index2]
            overlap_formula = \
                QuantifyingFormula(
                    quantified_formula=Conjunction(arguments=[argument1, argument2]),
                    variables=variables[:1],
                    quantifier=Quantifier.EXISTENTIAL)
            Negation(arguments=[overlap_formula], is_self_standing=True)
    
    # if (rdf_triple_subject, RDF.type, OWL.NamedIndividual) in owl_ontology:
    #     translate_rdf_triple_about_individual_subject_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
    #     return
    #
    # if rdf_triple_predicate == OWL.distinctMembers:
    #     translate_all_different_individuals_triple(all_differents_node=rdf_triple_object, owl_ontology=owl_ontology)
    #     return
    #
    # if __can_uri_be_cast_to_binary_predicate(uri=rdf_triple_subject, owl_ontology=owl_ontology) or __can_uri_be_cast_to_binary_predicate(uri=rdf_triple_object, owl_ontology=owl_ontology):
    #     translate_rdf_triple_about_property_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
    #     return
    #
    # if __can_uri_be_cast_to_unary_predicate(uri=rdf_triple_subject, owl_ontology=owl_ontology) or __can_uri_be_cast_to_unary_predicate(uri=rdf_triple_object, owl_ontology=owl_ontology):
    #     translate_rdf_triple_about_class_like_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
    #     return
    #
    # logging.warning(msg='Cannot migrate ' + str(rdf_triple))

