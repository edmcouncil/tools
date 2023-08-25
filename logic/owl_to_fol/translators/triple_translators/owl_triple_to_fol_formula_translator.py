from rdflib import OWL, URIRef, Graph

from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.disjunction import Disjunction
from logic.fol_logic.objects.equivalence import Equivalence
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.sw_node_to_fol_translator import get_subformula_from_node


def translate_owl_construct_to_fol_formula(owl_predicate: URIRef, sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    match owl_predicate:
        case OWL.disjointUnionOf:
            return __translate_disjointunionof(sw_arguments=sw_arguments, variables=variables, rdf_graph=rdf_graph)
        case OWL.equivalentClass:
            return __translate_equivalent(sw_arguments=sw_arguments, variables=variables, rdf_graph=rdf_graph)
        case OWL.inverseOf:
            return __translate_inverse_of(sw_arguments=sw_arguments, variables=variables, rdf_graph=rdf_graph)
        case OWL.disjointWith:
            return __translate_disjointWith(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.sameAs:
            return __translate_sameas(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.differentFrom:
            return __translate_differentFrom(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        

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


def __translate_equivalent(sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    if sw_arguments[0] in FormulaOriginRegistry.sw_to_fol_map:
        argument1 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[0]]
    else:
        argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    if sw_arguments[1] in FormulaOriginRegistry.sw_to_fol_map:
        argument2 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[1]]
    else:
        argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    formula = \
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[argument1, argument2]),
            variables=variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)

    return formula


def __translate_disjointunionof(sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    arguments_copy = sw_arguments.copy()
    union_sw_class = arguments_copy.pop(0)
    if union_sw_class in FormulaOriginRegistry.sw_to_fol_map:
        union_class_formula = FormulaOriginRegistry.sw_to_fol_map[union_sw_class]
    else:
        union_class_formula = get_subformula_from_node(node=union_sw_class, rdf_graph=rdf_graph, variables=variables)
    
    unioned_sw_classes= arguments_copy[0]
    unioned_formulae = list()
    for unioned_sw_class in unioned_sw_classes:
        if unioned_sw_class in FormulaOriginRegistry.sw_to_fol_map:
            unioned_formula = FormulaOriginRegistry.sw_to_fol_map[unioned_sw_class]
        else:
            unioned_formula = get_subformula_from_node(node=unioned_sw_class, rdf_graph=rdf_graph, variables=variables)
        unioned_formulae.append(unioned_formula)
        
    union_fol_disjunction = Disjunction(arguments=unioned_formulae)
    quantified_union_fol_disjunction = \
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[union_class_formula, union_fol_disjunction]),
            quantifier=Quantifier.UNIVERSAL,
            variables=Variable.get_next_variable_letter())
    
    conjuncts = list()
    for index1 in range(len(sw_arguments) - 1):
        argument1 = get_subformula_from_node(node=sw_arguments[index1], rdf_graph=rdf_graph, variables=variables)
        for index2 in range(index1 + 1, len(sw_arguments)):
            argument2 = get_subformula_from_node(node=sw_arguments[index2], rdf_graph=rdf_graph, variables=variables)
            overlap_formula = \
                QuantifyingFormula(
                    quantified_formula=Conjunction(arguments=[argument1, argument2]),
                    variables=Variable.get_next_variable_letter(),
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
        
