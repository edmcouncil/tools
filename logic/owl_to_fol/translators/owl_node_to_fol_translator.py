import logging

from rdflib import Graph, OWL, RDF
from rdflib.resource import Resource
from rdflib.term import Node, BNode, URIRef

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.disjunction import Disjunction
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.term import Term
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.translator_helpers import get_subformula_from_uri, get_fol_symbol_for_owl_node, \
    try_to_cast_bnode_as_typed_list


def get_simple_subformula_from_node(node: Node, owl_ontology: Graph, variable=Variable()) -> Formula:
    if isinstance(node, BNode):
        return get_subformula_from_bnode(bnode=node, owl_ontology=owl_ontology, variable=variable)
    if isinstance(node, URIRef):
       return get_subformula_from_uri(uri=node, owl_ontology=owl_ontology, variable=variable)


def get_subformula_from_bnode(bnode: BNode, owl_ontology: Graph, variable=Variable()) -> Formula:
    if (bnode, RDF.type, OWL.Restriction) in owl_ontology:
        formula = generate_fol_from_owl_restriction(owl_restriction=bnode, owl_ontology=owl_ontology, variable=variable)
        return formula
    
    if len(list(owl_ontology.objects(subject=bnode, predicate=OWL.inverseOf))) > 0:
        inversed_properties = list(owl_ontology.objects(subject=bnode, predicate=OWL.inverseOf))
        inversed_property_formula = get_simple_subformula_from_node(node=inversed_properties[0], owl_ontology=owl_ontology)
        formula = inversed_property_formula.swap_arguments(inplace=False)
        return formula
    
    if len(list(owl_ontology.subjects(object=bnode, predicate=OWL.propertyChainAxiom))) > 0:
        formula = __get_subformula_from_property_chain(bnode=bnode, owl_ontology=owl_ontology)
        return formula
    
    typed_list = try_to_cast_bnode_as_typed_list(bnode=bnode, owl_ontology=owl_ontology)
    
    if typed_list:
        if typed_list[0] == OWL.complementOf:
            formulas = [get_simple_subformula_from_node(node=typed_list[1],owl_ontology=owl_ontology, variable=variable)]
        else:
            formulas = get_listed_resources(rdf_list_object=typed_list[1],ontology=owl_ontology,rdf_list=list(),variable=variable)
        if typed_list[0] == OWL.unionOf:
            return Disjunction(arguments=formulas)
        if typed_list[0] == OWL.intersectionOf:
            return Conjunction(arguments=formulas)
        if typed_list[0] == OWL.complementOf:
            return Negation(arguments=formulas)
        if typed_list[0] == OWL.oneOf:
            return __get_one_of_formula(formulas=formulas)
    
    logging.warning(msg='Something is wrong with the list: ' + str(typed_list))


def generate_fol_from_owl_restriction(owl_restriction: Node, owl_ontology: Graph, variable: Term) -> Formula:
    owl_properties = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.onProperty))
    owl_property = owl_properties[0]
    owl_someValuesFrom = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.someValuesFrom))
    owl_allValuesFrom = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.allValuesFrom))
    owl_hasValue = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.hasValue))
    owl_onClass = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.onClass))
    owl_onDataRange = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.onDataRange))
    owl_onDatatype = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.onDatatype))
    owl_qualifiedCardinality = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.qualifiedCardinality))
    owl_cardinality = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.cardinality))
    owl_minCardinality = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.minCardinality))
    owl_maxCardinality = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.maxCardinality))
    owl_qualifiedMinCardinality = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.minQualifiedCardinality))
    owl_qualifiedMaxCardinality = list(owl_ontology.objects(subject=owl_restriction, predicate=OWL.maxQualifiedCardinality))
    variable_letter = Variable.get_next_variable_letter()
    if len(owl_someValuesFrom) > 0:
        restricting_node = owl_someValuesFrom[0]
        restricting_class_formula = get_simple_subformula_from_node(node=restricting_node, owl_ontology=owl_ontology, variable=Variable(letter=variable_letter))
        restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Conjunction(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.EXISTENTIAL,
                    variables=[Variable(letter=variable_letter)])
            return formula
        
    if len(owl_allValuesFrom) > 0:
        restricting_node = owl_allValuesFrom[0]
        restricting_class_formula = get_simple_subformula_from_node(node=restricting_node, owl_ontology=owl_ontology, variable=Variable(letter=variable_letter))
        restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Implication(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.UNIVERSAL,
                    variables=[Variable(letter=variable_letter)])
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
                owl_property=owl_property,
                restricting_node=restricting_node,
                owl_qualifiedMinCardinality=owl_qualifiedMinCardinality,
                owl_ontology=owl_ontology)
    if len(owl_minCardinality) > 0:
        formula = \
            __generate_fol_from_owl_min_unqualified_restriction(
                owl_property=owl_property,
                owl_minCardinality=owl_minCardinality,
                owl_ontology=owl_ontology)
    if len(owl_qualifiedMaxCardinality) > 0:
        formula = \
            __generate_fol_from_owl_max_qualified_restriction(
                owl_property=owl_property,
                restricting_node=restricting_node,
                owl_qualifiedMaxCardinality=owl_qualifiedMaxCardinality,
                owl_ontology=owl_ontology)
    if len(owl_maxCardinality) > 0:
        formula = \
            __generate_fol_from_owl_max_unqualified_restriction(
                owl_property=owl_property,
                owl_maxCardinality=owl_maxCardinality,
                owl_ontology=owl_ontology)
        
    if len(owl_qualifiedCardinality) > 0:
        max_formula = \
            __generate_fol_from_owl_max_qualified_restriction(
                owl_property=owl_property,
                restricting_node=restricting_node,
                owl_qualifiedMaxCardinality=owl_qualifiedCardinality,
                owl_ontology=owl_ontology)

        min_formula = \
            __generate_fol_from_owl_min_qualified_restriction(
                owl_property=owl_property,
                restricting_node=restricting_node,
                owl_qualifiedMinCardinality=owl_qualifiedCardinality,
                owl_ontology=owl_ontology)
        
        formula = Conjunction(arguments=[max_formula, min_formula])

    if len(owl_cardinality) > 0:
        max_formula = \
            __generate_fol_from_owl_max_unqualified_restriction(
                owl_property=owl_property,
                owl_maxCardinality=owl_cardinality,
                owl_ontology=owl_ontology)

        min_formula = \
            __generate_fol_from_owl_min_unqualified_restriction(
                owl_property=owl_property,
                owl_minCardinality=owl_cardinality,
                owl_ontology=owl_ontology)

        formula = Conjunction(arguments=[max_formula, min_formula])
        
    if len(owl_hasValue) > 0:
        restricting_relation_symbol = get_fol_symbol_for_owl_node(node=owl_property, owl_ontology=owl_ontology)
        restricting_individual_symbol = get_fol_symbol_for_owl_node(node=owl_hasValue[0], owl_ontology=owl_ontology)
        formula = AtomicFormula(predicate=restricting_relation_symbol, arguments=[variable, restricting_individual_symbol])
    
    if formula:
        return formula
    
    logging.warning(msg='Cannot get formula from a restriction')


def get_listed_resources(rdf_list_object: Resource, ontology: Graph, variable: Variable, rdf_list=list()) -> list:
    first_items_in_rdf_list = list(ontology.objects(subject=rdf_list_object, predicate=RDF.first))
    if len(first_items_in_rdf_list) == 0:
        return rdf_list
    resource = get_simple_subformula_from_node(node=first_items_in_rdf_list[0], owl_ontology=ontology, variable=variable)
    rdf_list.append(resource)
    rest_items_in_rdf_list = list(ontology.objects(subject=rdf_list_object, predicate=RDF.rest))
    rdf_list = get_listed_resources(rdf_list_object=rest_items_in_rdf_list[0], ontology=ontology, rdf_list=rdf_list, variable=variable)
    return rdf_list


def __generate_fol_from_owl_min_qualified_restriction(owl_property: Node, restricting_node, owl_qualifiedMinCardinality: list, owl_ontology: Graph) -> Formula:
    restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
    if restricting_relation_formula:
        if len(owl_qualifiedMinCardinality) > 0:
            minCardinality = int(owl_qualifiedMinCardinality[0])
            if minCardinality == 0:
                return IdentityFormula(arguments=[Variable(), Variable()])
            conjunction = None
            variables = list()
            index = 1
            while index <= minCardinality:
                variable = Variable(letter=Variable.get_next_variable_letter())
                restricting_class_formula = \
                    get_simple_subformula_from_node(
                        node=restricting_node,
                        owl_ontology=owl_ontology,
                        variable=variable)
                if not conjunction:
                    conjunction = Conjunction(
                        arguments=[restricting_relation_formula.replace_argument(argument=variable, index=1),restricting_class_formula])
                else:
                    conjunction = Conjunction(arguments=[conjunction, restricting_class_formula])
                    for backward_index in range(1, index):
                        conjunction = Conjunction(arguments=[conjunction, Negation(arguments=[IdentityFormula(arguments=[variables[-1], variable])])])
                variables.append(variable)
                index += 1
            formula = \
                QuantifyingFormula(
                    quantified_formula=conjunction,
                    quantifier=Quantifier.EXISTENTIAL,
                    variables=variables)
            return formula
        

def __generate_fol_from_owl_min_unqualified_restriction(owl_property: Node, owl_minCardinality: list, owl_ontology: Graph) -> Formula:
    restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
    if restricting_relation_formula:
        if len(owl_minCardinality) > 0:
            minCardinality = int(owl_minCardinality[0])
            if minCardinality == 0:
                return IdentityFormula(arguments=[Variable(), Variable()])
            conjunction = None
            variables = list()
            index = 1
            while index <= minCardinality:
                variable = Variable(letter=Variable.get_next_variable_letter())
                if not conjunction:
                    conjunction = restricting_relation_formula.replace_argument(argument=variable, index=1)
                else:
                    for backward_index in range(1, index):
                        conjunction = Conjunction(arguments=[conjunction, Negation(arguments=[IdentityFormula(arguments=[variables[-1], variable])])])
                variables.append(variable)
                index += 1
            formula = \
                QuantifyingFormula(
                    quantified_formula=conjunction,
                    quantifier=Quantifier.EXISTENTIAL,
                    variables=variables)
            return formula
        
        
def __generate_fol_from_owl_max_qualified_restriction(owl_property: Node, restricting_node, owl_qualifiedMaxCardinality: list, owl_ontology: Graph) -> Formula:
    next_variable_letter = Variable.get_next_variable_letter()
    restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
    if restricting_relation_formula:
        if len(owl_qualifiedMaxCardinality) > 0:
            maxCardinality = int(owl_qualifiedMaxCardinality[0])
            conjunction = None
            if maxCardinality == 0:
                restricting_class_formula = \
                    get_simple_subformula_from_node(
                        node=restricting_node,
                        owl_ontology=owl_ontology,
                        variable=Variable(letter=next_variable_letter))
                conjunction = Conjunction(arguments=[restricting_relation_formula.replace_argument(argument=Variable(letter=next_variable_letter), index=1), restricting_class_formula])
                formula = \
                    QuantifyingFormula(
                        quantified_formula=Negation(arguments=[conjunction]),
                        quantifier=Quantifier.UNIVERSAL,
                        variables=[Variable(letter=next_variable_letter)])
                return formula
            disjunction = None
            variables = list()
            index = 1
            while index <= maxCardinality + 1:
                indexed_variable_letter = Variable.get_next_variable_letter()
                variable = Variable(letter=indexed_variable_letter)
                restricting_class_formula = \
                    get_simple_subformula_from_node(
                        node=restricting_node,
                        owl_ontology=owl_ontology,
                        variable=variable)
                if not conjunction:
                    conjunction = Conjunction(arguments=[restricting_relation_formula.replace_argument(argument=variable, index=1),restricting_class_formula])
                else:
                    conjunction = Conjunction(arguments=[conjunction, restricting_relation_formula.replace_argument(argument=variable, index=1), restricting_class_formula])
                    for backward_index in range(1, index):
                        if not disjunction:
                            disjunction = IdentityFormula(arguments=[variables[-1], variable])
                        else:
                            disjunction = Disjunction(arguments=[disjunction, IdentityFormula(arguments=[variables[-1], variable])])
                variables.append(variable)
                index += 1
            formula = \
                QuantifyingFormula(
                    quantified_formula=Implication(arguments=[conjunction, disjunction]),
                    quantifier=Quantifier.UNIVERSAL,
                    variables=variables)
            return formula
        
        
def __generate_fol_from_owl_max_unqualified_restriction(owl_property: Node, owl_maxCardinality: list, owl_ontology: Graph) -> Formula:
    restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
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
            variables = list()
            index = 1
            while index <= maxCardinality + 1:
                variable = Variable(letter=Variable.get_next_variable_letter())
                if not conjunction:
                    conjunction = restricting_relation_formula.replace_argument(argument=variable, index=1)
                else:
                    conjunction = Conjunction(arguments=[conjunction, restricting_relation_formula.replace_argument(argument=variable, index=1)])
                    for backward_index in range(1, index):
                        if not disjunction:
                            disjunction = IdentityFormula(arguments=[variables[-1], variable])
                        else:
                            disjunction = Disjunction(arguments=[disjunction, IdentityFormula(arguments=[variables[-1], variable])])
                variables.append(variable)
                index += 1
            formula = \
                QuantifyingFormula(
                    quantified_formula=Implication(arguments=[conjunction, disjunction]),
                    quantifier=Quantifier.UNIVERSAL,
                    variables=variables)
            return formula
        
def __get_subformula_from_property_chain(bnode: BNode, owl_ontology: Graph) -> Formula:
    chained_formulas = list()
    first_variable_letter_in_formulas = Variable.get_next_variable_letter()
    second_variable_letter_in_formuals = Variable.get_next_variable_letter()
    variables = [Variable(letter=first_variable_letter_in_formulas), Variable(letter=second_variable_letter_in_formuals)]
    formulas = get_listed_resources(rdf_list_object=bnode, ontology=owl_ontology, rdf_list=list())
    first_formula = formulas[0]
    if first_formula.arguments[0] == first_variable_letter_in_formulas:
        replacement_index = 1
    else:
        replacement_index = 0
    last_index = 1
    initial_variable_in_chain = Variable.get_next_variable_letter()
    chained_formula = first_formula.replace_argument(argument=initial_variable_in_chain, index=replacement_index)
    chained_formulas.append(chained_formula)
    variables.append(initial_variable_in_chain)
    
    for index in range(1, len(formulas) - 1):
        formula = formulas[index]
        first_variable = variables[-1]
        second_variable = Variable.get_next_variable_letter()
        if formula.arguments[0].letter == first_variable_letter_in_formulas:
            first_replacement_index = 0
            second_replacement_index = 1
        else:
            first_replacement_index = 1
            second_replacement_index = 0
        chained_formula = formula.replace_argument(argument=first_variable, index=first_replacement_index)
        chained_formula = chained_formula.replace_argument(argument=second_variable, index=second_replacement_index)
        chained_formulas.append(chained_formula)
        variables.append(first_variable)
        variables.append(second_variable)
        last_index += 1
    
    last_formula = formulas[-1]
    if last_formula.arguments[0] == first_variable_letter_in_formulas:
        replacement_index = 0
    else:
        replacement_index = 1
    final_variable = variables[-1]
    chained_formula = last_formula.replace_argument(argument=final_variable, index=replacement_index)
    chained_formulas.append(chained_formula)
    variables.append(final_variable)
    
    chain = QuantifyingFormula(quantified_formula=Conjunction(arguments=chained_formulas), quantifier=Quantifier.EXISTENTIAL, variables=variables)
    return chain


def __get_one_of_formula(formulas: list) -> Formula:
    disjuncts = list()
    for index in range(len(formulas)):
        disjunct = IdentityFormula(arguments=[Variable(), Term(origin=formulas[index])])
        disjuncts.append(disjunct)
    one_of_disjunction = Disjunction(arguments=disjuncts)
    return one_of_disjunction