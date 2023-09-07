from rdflib import URIRef, RDFS, Graph

from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.node_translators.sw_node_to_fol_translator import get_subformula_from_node


def translate_rdfs_construct_to_fol_formula(rdfs_predicate: URIRef, sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    match rdfs_predicate:
        case RDFS.subClassOf:
            return __translate_subclassof(sw_arguments=sw_arguments, variables=variables, rdf_graph=rdf_graph)
        case RDFS.subPropertyOf:
            return __translate_subpropertyof(sw_arguments=sw_arguments, variables=variables, rdf_graph=rdf_graph)
        case RDFS.domain:
            return __translate_domain(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case RDFS.range:
            return __translate_range(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
    return None


def __translate_subclassof(sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    if sw_arguments[0] in FormulaOriginRegistry.sw_to_fol_map:
        argument1 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[0]]
    else:
        argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    if sw_arguments[1] in FormulaOriginRegistry.sw_to_fol_map:
        argument2 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[1]]
    else:
        argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    if not argument1 or not argument2:
        return None
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[argument1, argument2]),
            variables=variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_subpropertyof(sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[argument1, argument2]),
            variables=variables,
            quantifier=Quantifier.EXISTENTIAL)
    return formula
    

def __translate_domain(sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    if sw_arguments[1] in FormulaOriginRegistry.sw_to_fol_map:
        argument2 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[1]]
        argument2 = __adapt_variable_in_formula(formula=argument2, new_variable=variables[0])
    else:
        argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=[variables[0]])
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[argument1, argument2]),
            variables=variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_range(sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    argument1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    if sw_arguments[1] in FormulaOriginRegistry.sw_to_fol_map:
        argument2 = FormulaOriginRegistry.sw_to_fol_map[sw_arguments[1]]
        argument2 = __adapt_variable_in_formula(formula=argument2, new_variable=variables[1])
    else:
        argument2 = get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=[variables[1]])
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[argument1, argument2]),
            variables=variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula
    

def __adapt_variable_in_formula(formula: Formula, new_variable: Variable) -> Formula:
    free_variables_in_formula = formula.free_variables
    if not len(free_variables_in_formula) == 1:
        return None
    free_variable_in_formula = list(free_variables_in_formula)[0]
    formula_copy = formula.copy()
    formula_copy.replace_free_variable(old_variable=free_variable_in_formula, new_variable=new_variable)
    return formula_copy
    