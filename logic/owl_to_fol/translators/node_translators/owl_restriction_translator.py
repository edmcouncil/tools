import logging

from rdflib import Graph, OWL
from rdflib.term import Node

import logic.owl_to_fol.translators.node_translators.sw_node_to_fol_translator as sw_node_to_fol_translator
from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.disjunction import Disjunction
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.translator_getters import get_fol_symbol_for_owl_node


def generate_fol_from_owl_restriction(owl_restriction: Node, rdf_graph: Graph, variables: list) -> Formula:
    formula = None
    restricting_node = None
    
    owl_properties = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.onProperty))
    owl_property = owl_properties[0]
    owl_someValuesFrom = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.someValuesFrom))
    owl_allValuesFrom = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.allValuesFrom))
    owl_hasValue = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.hasValue))
    owl_onClass = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.onClass))
    owl_onDataRange = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.onDataRange))
    owl_onDatatype = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.onDatatype))
    owl_qualifiedCardinality = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.qualifiedCardinality))
    owl_cardinality = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.cardinality))
    owl_minCardinality = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.minCardinality))
    owl_maxCardinality = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.maxCardinality))
    owl_qualifiedMinCardinality = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.minQualifiedCardinality))
    owl_qualifiedMaxCardinality = list(rdf_graph.objects(subject=owl_restriction, predicate=OWL.maxQualifiedCardinality))
    
    if len(variables) == 0:
        variables.append(Variable.get_next_variable())
    if len(variables) == 1:
        variables.append(Variable.get_next_variable())
    restricted_variable = variables[1]
    restricting_relation_formula = sw_node_to_fol_translator.get_subformula_from_node(node=owl_property, rdf_graph=rdf_graph, variables=variables)

    if len(owl_someValuesFrom) > 0:
        restricting_node = owl_someValuesFrom[0]
        restricting_class_formula = sw_node_to_fol_translator.get_subformula_from_node(node=restricting_node, rdf_graph=rdf_graph, variables=[restricted_variable])
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Conjunction(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.EXISTENTIAL,
                    variables=[Variable(letter=restricted_variable)])
        
    if len(owl_allValuesFrom) > 0:
        restricting_node = owl_allValuesFrom[0]
        restricting_class_formula = sw_node_to_fol_translator.get_subformula_from_node(node=restricting_node, rdf_graph=rdf_graph, variables=[restricted_variable])
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Implication(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.UNIVERSAL,
                    variables=[Variable(letter=restricted_variable)])

    if len(owl_onClass) > 0:
        restricting_node = owl_onClass[0]
    if len(owl_onDataRange) > 0:
        restricting_node = owl_onDataRange[0]
    if len(owl_onDatatype) > 0:
        restricting_node = owl_onDatatype[0]
    
    if len(owl_qualifiedMinCardinality) > 0:
        formula = \
            __generate_fol_from_owl_min_qualified_restriction(
                restricting_node=restricting_node,
                restricting_relation_formula=restricting_relation_formula,
                restricted_variable=restricted_variable,
                owl_qualifiedMinCardinality=owl_qualifiedMinCardinality,
                owl_ontology=rdf_graph)
    if len(owl_minCardinality) > 0:
        formula = \
            __generate_fol_from_owl_min_unqualified_restriction(
                restricting_relation_formula=restricting_relation_formula,
                owl_minCardinality=owl_minCardinality)
    if len(owl_qualifiedMaxCardinality) > 0:
        formula = \
            __generate_fol_from_owl_max_qualified_restriction(
                restricting_node=restricting_node,
                restricting_relation_formula=restricting_relation_formula,
                restricted_variable=restricted_variable,
                owl_qualifiedMaxCardinality=owl_qualifiedMaxCardinality,
                owl_ontology=rdf_graph)
    if len(owl_maxCardinality) > 0:
        formula = \
            __generate_fol_from_owl_max_unqualified_restriction(
                restricting_relation_formula=restricting_relation_formula,
                owl_maxCardinality=owl_maxCardinality)
        
    if len(owl_qualifiedCardinality) > 0:
        max_formula = \
            __generate_fol_from_owl_max_qualified_restriction(
                restricting_node=restricting_node,
                restricting_relation_formula=restricting_relation_formula,
                restricted_variable=restricted_variable,
                owl_qualifiedMaxCardinality=owl_qualifiedCardinality,
                owl_ontology=rdf_graph)

        min_formula = \
            __generate_fol_from_owl_min_qualified_restriction(
                restricting_node=restricting_node,
                restricting_relation_formula=restricting_relation_formula,
                restricted_variable=restricted_variable,
                owl_qualifiedMinCardinality=owl_qualifiedCardinality,
                owl_ontology=rdf_graph)
        
        formula = Conjunction(arguments=[max_formula, min_formula])

    if len(owl_cardinality) > 0:
        max_formula = \
            __generate_fol_from_owl_max_unqualified_restriction(
                restricting_relation_formula=restricting_relation_formula,
                owl_maxCardinality=owl_cardinality)

        min_formula = \
            __generate_fol_from_owl_min_unqualified_restriction(
                restricting_relation_formula=restricting_relation_formula,
                owl_minCardinality=owl_cardinality)

        formula = Conjunction(arguments=[max_formula, min_formula])
        
    if len(owl_hasValue) > 0:
        restricting_relation_symbol = get_fol_symbol_for_owl_node(identifier=owl_property, rdf_graph=rdf_graph, arity=2)
        restricting_individual_symbol = get_fol_symbol_for_owl_node(identifier=owl_hasValue[0], rdf_graph=rdf_graph)
        formula = AtomicFormula(predicate=restricting_relation_symbol, arguments=[variables[0], restricting_individual_symbol])
    
    if formula:
        return formula
    
    logging.warning(msg='Cannot get formula from restriction ' + str(owl_restriction.skolemize()))


def __generate_fol_from_owl_min_qualified_restriction(
        restricting_node: Node,
        restricting_relation_formula: Formula,
        restricted_variable: Variable,
        owl_qualifiedMinCardinality: list,
        owl_ontology: Graph) -> Formula:
    if restricting_relation_formula:
        if len(owl_qualifiedMinCardinality) > 0:
            minCardinality = int(owl_qualifiedMinCardinality[0])
            if minCardinality == 0:
                identity_formula = IdentityFormula(arguments=[restricted_variable, restricted_variable])
                closed_identity_formula = \
                    QuantifyingFormula(
                        quantified_formula=identity_formula,
                        variables=identity_formula.free_variables,
                        quantifier=Quantifier.UNIVERSAL)
                return closed_identity_formula
            conjunction = None
            restricting_variables = list()
            index = 1
            while index <= minCardinality:
                restricting_variable = Variable.get_next_variable()
                restricting_class_formula = \
                    sw_node_to_fol_translator.get_subformula_from_node(
                        node=restricting_node,
                        rdf_graph=owl_ontology,
                        variables=[restricting_variable])
                if not conjunction:
                    conjunction = Conjunction(
                        arguments=[restricting_relation_formula.replace_argument(argument=restricting_variable, index=1),restricting_class_formula])
                else:
                    conjunction = Conjunction(arguments=[conjunction, restricting_class_formula])
                    for backward_index in range(1, index):
                        conjunction = Conjunction(arguments=[conjunction, Negation(arguments=[IdentityFormula(arguments=[restricting_variables[-1], restricting_variable])])])
                restricting_variables.append(restricting_variable)
                index += 1
            formula = \
                QuantifyingFormula(
                    quantified_formula=conjunction,
                    quantifier=Quantifier.EXISTENTIAL,
                    variables=restricting_variables)
            return formula


def __generate_fol_from_owl_min_unqualified_restriction(
        restricting_relation_formula: Formula,
        owl_minCardinality: list) -> Formula:
    if restricting_relation_formula:
        if len(owl_minCardinality) > 0:
            minCardinality = int(owl_minCardinality[0])
            if minCardinality == 0:
                return IdentityFormula(arguments=[Variable(), Variable()])
            conjunction = None
            restricting_variables = list()
            index = 1
            while index <= minCardinality:
                restricting_variable = Variable.get_next_variable()
                if not conjunction:
                    conjunction = restricting_relation_formula.replace_argument(argument=restricting_variable, index=1)
                else:
                    for backward_index in range(1, index):
                        conjunction = Conjunction(arguments=[conjunction, Negation(arguments=[IdentityFormula(arguments=[restricting_variables[-1], restricting_variable])])])
                restricting_variables.append(restricting_variable)
                index += 1
            formula = \
                QuantifyingFormula(
                    quantified_formula=conjunction,
                    quantifier=Quantifier.EXISTENTIAL,
                    variables=restricting_variables)
            return formula


def __generate_fol_from_owl_max_qualified_restriction(
        restricting_node: Node,
        restricting_relation_formula: Formula,
        restricted_variable: Variable,
        owl_qualifiedMaxCardinality: list,
        owl_ontology: Graph) -> Formula:
    if restricting_relation_formula:
        if len(owl_qualifiedMaxCardinality) > 0:
            maxCardinality = int(owl_qualifiedMaxCardinality[0])
            conjunction = None
            if maxCardinality == 0:
                restricting_class_formula = \
                    sw_node_to_fol_translator.get_subformula_from_node(
                        node=restricting_node,
                        rdf_graph=owl_ontology,
                        variables=[restricted_variable])
                conjunction = Conjunction(arguments=[restricting_relation_formula.replace_argument(argument=restricted_variable, index=1), restricting_class_formula])
                formula = \
                    QuantifyingFormula(
                        quantified_formula=Negation(arguments=[conjunction]),
                        quantifier=Quantifier.UNIVERSAL,
                        variables=[restricted_variable])
                return formula
            disjunction = None
            restricting_variables = list()
            index = 1
            while index <= maxCardinality + 1:
                indexed_variable_letter = Variable.get_next_variable()
                restricting_variable = Variable(letter=indexed_variable_letter)
                restricting_class_formula = \
                    sw_node_to_fol_translator.get_subformula_from_node(
                        node=restricting_node,
                        rdf_graph=owl_ontology,
                        variables=[restricting_variable])
                if not conjunction:
                    conjunction = Conjunction(arguments=[restricting_relation_formula.replace_argument(argument=restricting_variable, index=1),restricting_class_formula])
                else:
                    conjunction = Conjunction(arguments=[conjunction, restricting_relation_formula.replace_argument(argument=restricting_variable, index=1), restricting_class_formula])
                    for backward_index in range(1, index):
                        if not disjunction:
                            disjunction = IdentityFormula(arguments=[restricting_variables[-1], restricting_variable])
                        else:
                            disjunction = Disjunction(arguments=[disjunction, IdentityFormula(arguments=[restricting_variables[-1], restricting_variable])])
                restricting_variables.append(restricting_variable)
                index += 1
            formula = \
                QuantifyingFormula(
                    quantified_formula=Implication(arguments=[conjunction, disjunction]),
                    quantifier=Quantifier.UNIVERSAL,
                    variables=restricting_variables)
            return formula


def __generate_fol_from_owl_max_unqualified_restriction(
        restricting_relation_formula: Formula,
        owl_maxCardinality: list) -> Formula:
    if restricting_relation_formula:
        if len(owl_maxCardinality) > 0:
            maxCardinality = int(owl_maxCardinality[0])
            if maxCardinality == 0:
                formula = \
                    QuantifyingFormula(
                        quantified_formula=Negation(arguments=[restricting_relation_formula.replace_argument(argument=Variable.get_next_variable(), index=1)]),
                        quantifier=Quantifier.UNIVERSAL,
                        variables=[Variable.get_next_variable()])
                return formula
            conjunction = None
            disjunction = None
            restricting_variables = list()
            index = 1
            while index <= maxCardinality + 1:
                restricting_variable = Variable.get_next_variable()
                if not conjunction:
                    conjunction = restricting_relation_formula.replace_argument(argument=restricting_variable, index=1)
                else:
                    conjunction = Conjunction(arguments=[conjunction, restricting_relation_formula.replace_argument(argument=restricting_variable, index=1)])
                    for backward_index in range(1, index):
                        if not disjunction:
                            disjunction = IdentityFormula(arguments=[restricting_variables[-1], restricting_variable])
                        else:
                            disjunction = Disjunction(arguments=[disjunction, IdentityFormula(arguments=[restricting_variables[-1], restricting_variable])])
                restricting_variables.append(restricting_variable)
                index += 1
            formula = \
                QuantifyingFormula(
                    quantified_formula=Implication(arguments=[conjunction, disjunction]),
                    quantifier=Quantifier.UNIVERSAL,
                    variables=restricting_variables)
            return formula
