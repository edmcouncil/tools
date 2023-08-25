import logging

from rdflib import URIRef, Graph, BNode, RDF, OWL
from rdflib.term import Node
from typing_extensions import Optional

import logic.owl_to_fol.translators.triple_translators.sw_to_fol_helper
from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.disjunction import Disjunction
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.predicate import Predicate
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.term import Term
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.translator_helpers import __can_uri_be_cast_to_unary_predicate, \
    __can_uri_be_cast_to_binary_predicate, __can_uri_be_cast_to_term, get_fol_symbol_for_owl_node


def get_subformula_from_uri(uri: URIRef, owl_ontology: Graph, variables: list) -> Formula:
    if __can_uri_be_cast_to_unary_predicate(uri=uri, owl_ontology=owl_ontology):
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin=uri, arity=1)
        return \
            AtomicFormula(predicate=predicate, arguments=variables[:1])
    
    if __can_uri_be_cast_to_binary_predicate(uri=uri, owl_ontology=owl_ontology):
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin=uri, arity=2)
        return \
            AtomicFormula(predicate=predicate, arguments=variables)
    
    if __can_uri_be_cast_to_term(uri=uri, owl_ontology=owl_ontology):
        if uri in Term.registry:
            term = Term.registry[uri]
        else:
            term = Term(origin=uri)
        return term
    
    logging.warning(msg='Cannot get formula from ' + str(uri))


def get_subformula_from_node(node: Node, rdf_graph: Graph, variables: list) -> Optional[Formula]:
    if isinstance(node, BNode):
        return get_subformula_from_bnode(bnode=node, rdf_graph=rdf_graph, variables=variables)
    if isinstance(node, URIRef):
        return get_subformula_from_uri(uri=node, owl_ontology=rdf_graph, variables=variables)


def get_subformula_from_bnode(bnode: BNode, rdf_graph: Graph, variables: list) -> Optional[Formula]:
    bnode_predictes_objects = list(rdf_graph.predicate_objects(subject=bnode))
    bnodes_triples = list()
    for bnode_predicte, bnode_object in bnode_predictes_objects:
        if not logic.owl_to_fol.translators.triple_translators.sw_to_fol_helper.is_triple_out_of_scope(sw_triple=(bnode, bnode_predicte, bnode_object), rdf_graph=rdf_graph):
            bnodes_triples.append((bnode, bnode_predicte, bnode_object))
            
    if len(bnodes_triples) == 1:
        # formula = sw_triple_to_fol_translator.translate_sw_triple_to_fol(sw_triple=bnodes_triples[0],rdf_graph=rdf_graph,variables=variables)
        # return formula
        return None
    else:
        if (bnode, RDF.type, OWL.Restriction) in rdf_graph:
            formula = generate_fol_from_owl_restriction(owl_restriction=bnode, rdf_graph=rdf_graph, variables=variables)
            FormulaOriginRegistry.sw_to_fol_map[bnode] = formula
            return formula
        # else:
        #     v=0
    #
    # if len(list(owl_ontology.objects(subject=bnode, predicate=OWL.inverseOf))) > 0:
    #     inversed_properties = list(owl_ontology.objects(subject=bnode, predicate=OWL.inverseOf))
    #     inversed_property_formula = get_subformula_from_node(node=inversed_properties[0], owl_ontology=owl_ontology, variables=variables)
    #     if isinstance(inversed_property_formula, AtomicFormula):
    #         formula = inversed_property_formula.swap_arguments(inplace=False)
    #         return formula
    #
    # if len(list(owl_ontology.subjects(object=bnode, predicate=OWL.propertyChainAxiom))) > 0:
    #     formula = __get_subformula_from_property_chain(bnode=bnode, owl_ontology=owl_ontology, variables=variables)
    #     return formula
    #
    # typed_list = try_to_cast_bnode_as_typed_list(bnode=bnode, owl_ontology=owl_ontology)
    #
    # if typed_list:
    #     if typed_list[0] == OWL.complementOf:
    #         formulas = [get_subformula_from_node(node=typed_list[1], owl_ontology=owl_ontology, variables=variables)]
    #     else:
    #         formulas = get_listed_resources(rdf_list_object=typed_list[1], ontology=owl_ontology, rdf_list=list(), variables=variables)
    #     if typed_list[0] == OWL.unionOf:
    #         return Disjunction(arguments=formulas)
    #     if typed_list[0] == OWL.intersectionOf:
    #         return Conjunction(arguments=formulas)
    #     if typed_list[0] == OWL.complementOf:
    #         return Negation(arguments=formulas)
    #     if typed_list[0] == OWL.oneOf:
    #         return __get_one_of_formula(formulas=formulas)
    #     if typed_list[0] == OWL.distinctMembers:
    #         return None
    #
    # listed_resources = get_listed_resources(rdf_list_object=bnode, ontology=owl_ontology, variables=variables, rdf_list=list())
    #
    # if len(listed_resources) > 0:
    #     return listed_resources
    #
    # logging.warning(msg='Not yet implemented: ' + str(typed_list))


def generate_fol_from_owl_restriction(owl_restriction: Node, rdf_graph: Graph, variables: list) -> Formula:
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
    
    restricted_variable = Variable(letter=Variable.get_next_variable_letter())
    restricting_relation_formula = get_subformula_from_node(node=owl_property, rdf_graph=rdf_graph, variables=variables + [restricted_variable])

    if len(owl_someValuesFrom) > 0:
        restricting_node = owl_someValuesFrom[0]
        restricting_class_formula = get_subformula_from_node(node=restricting_node, rdf_graph=rdf_graph, variables=[restricted_variable])
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Conjunction(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.EXISTENTIAL,
                    variables=[Variable(letter=restricted_variable)])
            return formula
        
    if len(owl_allValuesFrom) > 0:
        restricting_node = owl_allValuesFrom[0]
        restricting_class_formula = get_subformula_from_node(node=restricting_node, rdf_graph=rdf_graph, variables=[restricted_variable])
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Implication(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.UNIVERSAL,
                    variables=[Variable(letter=restricted_variable)])
            return formula

    formula = None
    restricting_node = None
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
        restricting_relation_symbol = get_fol_symbol_for_owl_node(node=owl_property, rdf_graph=rdf_graph)
        restricting_individual_symbol = get_fol_symbol_for_owl_node(node=owl_hasValue[0], rdf_graph=rdf_graph)
        formula = AtomicFormula(predicate=restricting_relation_symbol, arguments=[variables[0], restricting_individual_symbol])
    
    if formula:
        return formula
    
    logging.warning(msg='Cannot get formula from a restriction')


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
                restricting_variable = Variable(letter=Variable.get_next_variable_letter())
                restricting_class_formula = \
                    get_subformula_from_node(
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
                restricting_variable = Variable(letter=Variable.get_next_variable_letter())
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
                    get_subformula_from_node(
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
                indexed_variable_letter = Variable.get_next_variable_letter()
                restricting_variable = Variable(letter=indexed_variable_letter)
                restricting_class_formula = \
                    get_subformula_from_node(
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
                        quantified_formula=Negation(arguments=[restricting_relation_formula.replace_argument(argument=Variable(letter=Variable.get_next_variable_letter()), index=1)]),
                        quantifier=Quantifier.UNIVERSAL,
                        variables=[Variable(letter=Variable.get_next_variable_letter())])
                return formula
            conjunction = None
            disjunction = None
            restricting_variables = list()
            index = 1
            while index <= maxCardinality + 1:
                restricting_variable = Variable(letter=Variable.get_next_variable_letter())
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


def get_fol_formulae_from_rdf_list(rdf_list_object: Node, rdf_graph: Graph, variables: list, fol_formulae: list) -> list:
    first_items_in_rdf_list = list(rdf_graph.objects(subject=rdf_list_object, predicate=RDF.first))
    if len(first_items_in_rdf_list) == 0:
        return fol_formulae
    fol_formula = get_subformula_from_node(node=first_items_in_rdf_list[0], rdf_graph=rdf_graph, variables=variables)
    fol_formulae.append(fol_formula)
    rest_items_in_rdf_list = list(rdf_graph.objects(subject=rdf_list_object, predicate=RDF.rest))
    fol_formulae = get_fol_formulae_from_rdf_list(rdf_list_object=rest_items_in_rdf_list[0], rdf_graph=rdf_graph, fol_formulae=fol_formulae, variables=variables)
    return fol_formulae


def get_fol_terms_from_rdf_list(rdf_list_object: Node, rdf_graph: Graph, fol_terms: list) -> list:
    first_items_in_rdf_list = list(rdf_graph.objects(subject=rdf_list_object, predicate=RDF.first))
    if len(first_items_in_rdf_list) == 0:
        return fol_terms
    fol_term = get_fol_symbol_for_owl_node(node=first_items_in_rdf_list[0], rdf_graph=rdf_graph)
    fol_terms.append(fol_term)
    rest_items_in_rdf_list = list(rdf_graph.objects(subject=rdf_list_object, predicate=RDF.rest))
    fol_terms = get_fol_terms_from_rdf_list(rdf_list_object=rest_items_in_rdf_list[0], rdf_graph=rdf_graph, fol_terms=fol_terms)
    return fol_terms



