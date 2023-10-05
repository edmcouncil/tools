from rdflib import URIRef, RDF, Graph, OWL

from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.node_translators.sw_node_to_fol_translator import get_subformula_from_node
from logic.owl_to_fol.translators.triple_translators.custom_triple_to_fol_formula_translator import \
    translate_custom_construct_to_self_standing_fol_formula
from rdflib import URIRef, RDF, Graph, OWL

from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.node_translators.sw_node_to_fol_translator import get_subformula_from_node
from logic.owl_to_fol.translators.triple_translators.custom_triple_to_fol_formula_translator import \
    translate_custom_construct_to_self_standing_fol_formula


def translate_rdf_construct_to_fol_formula(rdf_predicate: URIRef, sw_arguments: list, rdf_graph: Graph) -> Formula:
    match rdf_predicate:
        case RDF.type : return __translate_rdf_type(sw_arguments=sw_arguments, rdf_graph=rdf_graph)


def __translate_rdf_type(sw_arguments: list, rdf_graph: Graph) -> Formula:
    sw_type = sw_arguments[1]
    match sw_type:
        case OWL.NamedIndividual:
            return __translate_namedIndividual(sw_arguments=sw_arguments, rdf_graph=rdf_graph)
        case OWL.ReflexiveProperty:
            return __translate_reflexiveProperty(sw_arguments=sw_arguments, rdf_graph=rdf_graph)
        case OWL.IrreflexiveProperty:
            return __translate_irreflexiveProperty(sw_arguments=sw_arguments, rdf_graph=rdf_graph)
        case OWL.TransitiveProperty:
            return __translate_transitiveProperty(sw_arguments=sw_arguments, rdf_graph=rdf_graph)
        case OWL.SymmetricProperty:
            return __translate_symmetricProperty(sw_arguments=sw_arguments, rdf_graph=rdf_graph)
        case OWL.AsymmetricProperty:
            return __translate_asymmetricProperty(sw_arguments=sw_arguments, rdf_graph=rdf_graph)
        case OWL.FunctionalProperty:
            return __translate_functionalProperty(sw_arguments=sw_arguments, rdf_graph=rdf_graph)
        case OWL.InverseFunctionalProperty:
            return __translate_inversefunctionalProperty(sw_arguments=sw_arguments, rdf_graph=rdf_graph)


def __translate_namedIndividual(sw_arguments: list, rdf_graph: Graph):
    formula = translate_custom_construct_to_self_standing_fol_formula(sw_triple=(sw_arguments[0], RDF.type, sw_arguments[1]), rdf_graph=rdf_graph)
    return formula

def __translate_transitiveProperty(sw_arguments: list, rdf_graph: Graph):
    first_variable = Variable.get_next_variable()
    second_variable = Variable.get_next_variable()
    third_variable = Variable.get_next_variable()
    property_formula_1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph,variables=[first_variable, second_variable])
    property_formula_2 = property_formula_1.replace_arguments(arguments=[second_variable, third_variable])
    property_formula_3 = property_formula_1.replace_arguments(arguments=[first_variable, third_variable])
    quantifying_variables = [first_variable, second_variable, third_variable]
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(
            arguments=[Conjunction(arguments=[property_formula_1, property_formula_2]), property_formula_3]),
            variables=quantifying_variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_functionalProperty(sw_arguments: list, rdf_graph: Graph):
    first_variable = Variable.get_next_variable()
    second_variable = Variable.get_next_variable()
    third_variable = Variable.get_next_variable()
    property_formula_1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph,variables=[first_variable, second_variable])
    property_formula_2 = property_formula_1.replace_arguments(arguments=[first_variable, third_variable])
    identity_formula = IdentityFormula(arguments=[second_variable, third_variable])
    quantifying_variables = [first_variable, second_variable, third_variable]
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(
                arguments=[Conjunction(arguments=[property_formula_1, property_formula_2]), identity_formula]),
            variables=quantifying_variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_inversefunctionalProperty(sw_arguments: list, rdf_graph: Graph):
    first_variable = Variable.get_next_variable()
    second_variable = Variable.get_next_variable()
    third_variable = Variable.get_next_variable()
    property_formula_1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph,variables=[first_variable, second_variable])
    property_formula_2 = property_formula_1.replace_arguments(arguments=[third_variable, second_variable])
    identity_formula = IdentityFormula(arguments=[first_variable, third_variable])
    quantifying_variables = [first_variable, second_variable, third_variable]
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(
                arguments=[Conjunction(arguments=[property_formula_1, property_formula_2]), identity_formula]),
            variables=quantifying_variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_symmetricProperty(sw_arguments: list, rdf_graph: Graph):
    first_variable = Variable.get_next_variable()
    second_variable = Variable.get_next_variable()
    property_formula_1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph,variables=[first_variable, second_variable])
    property_formula_2 = property_formula_1.replace_arguments(arguments=[second_variable, first_variable])
    quantifying_variables = [first_variable, second_variable]
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[property_formula_1, property_formula_2]),
            variables=quantifying_variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_reflexiveProperty(sw_arguments: list, rdf_graph: Graph):
    first_variable = Variable.get_next_variable()
    property_formula_1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph,variables=[first_variable])
    quantifying_variables = [first_variable]
    formula = \
        QuantifyingFormula(
            quantified_formula=property_formula_1,
            variables=quantifying_variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_irreflexiveProperty(sw_arguments: list, rdf_graph: Graph):
    first_variable = Variable.get_next_variable()
    property_formula = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph,variables=[first_variable])
    quantifying_variables = [first_variable]
    formula = \
        QuantifyingFormula(
            quantified_formula=Negation(arguments=[property_formula]),
            variables=quantifying_variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula


def __translate_asymmetricProperty(sw_arguments: list, rdf_graph: Graph):
    first_variable = Variable.get_next_variable()
    second_variable = Variable.get_next_variable()
    property_formula_1 = get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph,variables=[first_variable, second_variable])
    property_formula_2 = property_formula_1.replace_arguments(arguments=[second_variable, first_variable])
    quantifying_variables = [first_variable, second_variable]
    formula = \
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[property_formula_1, Negation(arguments=[property_formula_2])]),
            variables=quantifying_variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return formula