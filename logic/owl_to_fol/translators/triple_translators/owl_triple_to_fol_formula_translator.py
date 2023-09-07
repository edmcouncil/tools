import logging

from rdflib import OWL, URIRef, Graph

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.disjunction import Disjunction
from logic.fol_logic.objects.equivalence import Equivalence
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.node_translators import sw_node_to_fol_translator
from logic.owl_to_fol.translators.node_translators.sw_node_to_fol_translator import get_subformula_from_node, \
    get_fol_formulae_from_rdf_list


def translate_owl_construct_to_fol_formula(owl_predicate: URIRef, sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    match owl_predicate:
        case OWL.disjointUnionOf:
            return __translate_disjointunionof(sw_arguments=sw_arguments, variables=variables, rdf_graph=rdf_graph)
        case OWL.equivalentClass:
            return __translate_equivalentClass(sw_arguments=sw_arguments, variables=variables, rdf_graph=rdf_graph)
        case OWL.inverseOf:
            return __translate_inverse_of(sw_arguments=sw_arguments, variables=variables, rdf_graph=rdf_graph)
        case OWL.disjointWith:
            return __translate_disjointWith(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.propertyDisjointWith:
            return __translate_propertyDisjointWith(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.sameAs:
            return __translate_sameas(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.differentFrom:
            return __translate_differentFrom(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.propertyChainAxiom:
            return __translate_propertyChainAxiom(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
  

def __translate_inverse_of(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    argument1 = get_subformula_from_node(node=sw_arguments[0],rdf_graph=rdf_graph, variables=variables)
    argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    inverse_argument2 = argument2.swap_arguments()
    formula = \
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[argument1, inverse_argument2]),
            variables=variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_equivalentClass(sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    if sw_arguments[0] in FormulaOriginRegistry.sw_to_fol_map:
        argument1 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[0]]
    else:
        argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    if sw_arguments[1] in FormulaOriginRegistry.sw_to_fol_map:
        argument2 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[1]]
    else:
        argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    if not argument1 or not argument2:
        logging.warning(
            msg='Cannot process owl class equivalence relation between: ' + '|'.join([sw_arguments[0], sw_arguments[1]]))
        return
    formula = \
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[argument1, argument2]),
            variables=variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_disjointunionof(sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    union_class_formula = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    unioned_class_formulae = get_fol_formulae_from_rdf_list(rdf_list_object=sw_arguments[1], rdf_graph=rdf_graph,variables=variables, fol_formulae=list())
    unioned_classed_disjunction = Disjunction(arguments=unioned_class_formulae)
    
    quantified_union_fol_disjunction = \
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[union_class_formula, unioned_classed_disjunction]),
            quantifier=Quantifier.UNIVERSAL,
            variables=[Variable.get_next_variable()])
    
    conjuncts = list()
    for unioned_class_formula1 in unioned_class_formulae:
        for unioned_class_formula2 in unioned_class_formulae:
            if not unioned_class_formula1 == unioned_class_formula2:
                overlap_formula = \
                    QuantifyingFormula(
                        quantified_formula=Conjunction(arguments=[unioned_class_formula1, unioned_class_formula2]),
                        variables=variables,
                        quantifier=Quantifier.EXISTENTIAL)
                conjunct = Negation(arguments=[overlap_formula])
                conjuncts.append(conjunct)
            
    union_fol_disjointness = Conjunction(arguments=conjuncts)
    formula = Conjunction(arguments=[quantified_union_fol_disjunction, union_fol_disjointness], is_self_standing=True)
    return formula

def __translate_disjointWith(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    if sw_arguments[0] in FormulaOriginRegistry.sw_to_fol_map:
        argument1 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[0]]
    else:
        argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    if sw_arguments[1] in FormulaOriginRegistry.sw_to_fol_map:
        argument2 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[1]]
    else:
        argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    overlap_formula = \
        QuantifyingFormula(
            quantified_formula=Conjunction(arguments=[argument1, argument2]),
            variables=variables,
            quantifier=Quantifier.EXISTENTIAL)
    formula = Negation(arguments=[overlap_formula])
    return formula


def __translate_propertyDisjointWith(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    overlap_formula = \
        QuantifyingFormula(
            quantified_formula=Conjunction(arguments=[argument1, argument2]),
            variables=variables,
            quantifier=Quantifier.EXISTENTIAL)
    formula = Negation(arguments=[overlap_formula])
    return formula
    
    
def __translate_sameas(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    formula = IdentityFormula(arguments=[argument1, argument2], is_self_standing=True)
    return formula


def __translate_differentFrom(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    formula = Negation(arguments=[IdentityFormula(arguments=[argument1, argument2], is_self_standing=True)])
    return formula


def __translate_propertyChainAxiom(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    subproperty_formula = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    chained_properties = sw_node_to_fol_translator.get_fol_terms_from_rdf_list(rdf_list_object=sw_arguments[1],rdf_graph=rdf_graph, fol_terms=list())
    chain_links = list()
    chained_variables = set()
    last_second_variable_used = variables[1]
    for index in range(len(chained_properties)):
        if index == 0:
            first_argument = variables[0]
            second_argument = Variable.get_next_variable()
            last_second_variable_used = second_argument
            chained_variables.add(second_argument)
        elif index == len(chained_properties) - 1:
            first_argument = last_second_variable_used
            second_argument = variables[1]
            last_second_variable_used = second_argument
            chained_variables.add(first_argument)
        else:
            first_argument = last_second_variable_used
            second_argument = Variable.get_next_variable()
            last_second_variable_used = second_argument
            chained_variables.add(first_argument)
            chained_variables.add(second_argument)
        chain_link = AtomicFormula(predicate=chained_properties[index],arguments=[first_argument, second_argument])
        chain_links.append(chain_link)
    chain_links_conjunction = Conjunction(arguments=chain_links)
    chain_formula = \
        QuantifyingFormula(
            quantified_formula=chain_links_conjunction,
            variables=list(chained_variables),
            quantifier=Quantifier.EXISTENTIAL)
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[chain_formula, subproperty_formula]),
            variables=variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula
    

