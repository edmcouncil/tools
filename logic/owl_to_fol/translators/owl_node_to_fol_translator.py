from rdflib import Graph, OWL
from rdflib.term import Node, BNode

from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.sw_node_to_fol_translator import get_fol_formulae_from_rdf_list


def __get_subformula_from_property_chain(bnode: BNode, owl_ontology: Graph, variables: list) -> Formula:
    chained_formulas = list()
    chained_variables = list()
    formulas = get_fol_formulae_from_rdf_list(rdf_list_object=bnode, rdf_graph=owl_ontology, fol_formulae=list(), variables=variables)
    first_formula = formulas[0]
    initial_variable_in_chain = Variable(letter=Variable.get_next_variable_letter())
    chained_formula = first_formula.replace_argument(argument=initial_variable_in_chain, index=1)
    chained_formulas.append(chained_formula)
    chained_variables.append(initial_variable_in_chain)
    
    for index in range(1, len(formulas) - 1):
        formula = formulas[index]
        first_variable = chained_variables[-1]
        second_variable = Variable(letter=Variable.get_next_variable_letter())
        chained_formula = formula.replace_argument(argument=first_variable, index=0)
        chained_formula = chained_formula.replace_argument(argument=second_variable, index=1)
        chained_formulas.append(chained_formula)
        chained_variables.append(second_variable)
        
    last_formula = formulas[-1]
    final_variable = chained_variables[-1]
    chained_formula = last_formula.replace_argument(final_variable, index=0)
    chained_formulas.append(chained_formula)
    chain = QuantifyingFormula(quantified_formula=Conjunction(arguments=chained_formulas), quantifier=Quantifier.EXISTENTIAL, variables=chained_variables)
    return chain


# def __get_one_of_formula(formulas: list) -> Formula:
#     disjuncts = list()
#     for index in range(len(formulas)):
#         disjunct = IdentityFormula(arguments=[Variable(), Term(origin=formulas[index])])
#         disjuncts.append(disjunct)
#     one_of_disjunction = Disjunction(arguments=disjuncts)
#     return one_of_disjunction


def translate_all_different_individuals_triple(all_differents_node: Node, owl_ontology:Graph):
    different_individuals = get_fol_formulae_from_rdf_list(rdf_list_object=all_differents_node, rdf_graph=owl_ontology, variables=list(), fol_formulae=list())
    for index1 in range(len(different_individuals)-1):
        node1 = different_individuals[index1]
        for index2 in range(index1+1, len(different_individuals)):
            node2 = different_individuals[index2]
            Negation(arguments=[IdentityFormula(arguments=[node1, node2])], is_self_standing=True)
            
            
def translate_all_disjoint_classes_triple(all_disjoint_classes_node: Node, owl_ontology:Graph, variable: Variable):
    all_disjoint_classess = list(owl_ontology.objects(subject=all_disjoint_classes_node, predicate=OWL.members))[0]
    different_classes = get_fol_formulae_from_rdf_list(rdf_list_object=all_disjoint_classess, rdf_graph=owl_ontology, variables=[variable], fol_formulae=list())
    for index1 in range(len(different_classes)-1):
        class1 = different_classes[index1]
        for index2 in range(index1+1, len(different_classes)):
            class2 = different_classes[index2]
            overlap_formula = \
                QuantifyingFormula(
                    quantified_formula=Conjunction(arguments=[class1, class2]),
                    variables=[variable],
                    quantifier=Quantifier.EXISTENTIAL)
            Negation(arguments=[overlap_formula], is_self_standing=True)
            
    