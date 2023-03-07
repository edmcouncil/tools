import logging

from rdflib import Graph, OWL, RDF, RDFS
from rdflib.resource import Resource
from rdflib.term import Node, BNode, URIRef

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.variable import Variable, TPTP_DEFAULT_LETTER_1, TPTP_DEFAULT_LETTER_2, \
    TPTP_DEFAULT_LETTER_3
from logic.fol_logic.objects.disjunction import Disjunction
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.predicate import Predicate
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.symbol import Symbol
from logic.fol_logic.objects.term import Term

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
        chained_formulas = list()
        variables = [Variable(letter=TPTP_DEFAULT_LETTER_1), Variable(letter=TPTP_DEFAULT_LETTER_2)]
        formulas = get_listed_resources(rdf_list_object=bnode, ontology=owl_ontology, rdf_list=list())
        first_formula = formulas[0]
        if first_formula.arguments[0] == TPTP_DEFAULT_LETTER_1:
            replacement_index = 1
        else:
            replacement_index = 0
        last_index = 1
        initial_variable = Variable(letter=TPTP_DEFAULT_LETTER_3+str(last_index))
        chained_formula = first_formula.replace_argument(argument=initial_variable,index=replacement_index)
        chained_formulas.append(chained_formula)
        variables.append(initial_variable)
        
        for index in range(1,len(formulas)-1):
            formula = formulas[index]
            first_variable = Variable(TPTP_DEFAULT_LETTER_3 + str(last_index))
            second_variable = Variable(TPTP_DEFAULT_LETTER_3 + str(last_index + 1))
            if formula.arguments[0].letter == TPTP_DEFAULT_LETTER_1:
                first_replacement_index = 0
                second_replacement_index = 1
            else:
                first_replacement_index = 1
                second_replacement_index = 0
            chained_formula = formula.replace_argument(argument=first_variable, index=first_replacement_index)
            chained_formula = chained_formula.replace_argument(argument=second_variable,index=second_replacement_index)
            chained_formulas.append(chained_formula)
            variables.append(first_variable)
            variables.append(second_variable)
            last_index += 1

        last_formula = formulas[-1]
        if last_formula.arguments[0] == TPTP_DEFAULT_LETTER_1:
            replacement_index = 0
        else:
            replacement_index = 1
        final_variable = Variable(letter=TPTP_DEFAULT_LETTER_3 + str(last_index))
        chained_formula = last_formula.replace_argument(argument=final_variable,index=replacement_index)
        chained_formulas.append(chained_formula)
        variables.append(final_variable)
        
        chain = QuantifyingFormula(quantified_formula=Conjunction(arguments=chained_formulas), quantifier=Quantifier.EXISTENTIAL,variables=variables)
        return chain

    typed_list = try_to_cast_bnode_as_typed_list(bnode=bnode, owl_ontology=owl_ontology)
    
    if typed_list:
        if typed_list[0] == OWL.complementOf:
            formulas = [get_simple_subformula_from_node(node=typed_list[1],owl_ontology=owl_ontology)]
        else:
            formulas = get_listed_resources(rdf_list_object=typed_list[1],ontology=owl_ontology,rdf_list=list())
        if typed_list[0] == OWL.unionOf:
            return Disjunction(arguments=formulas)
        if typed_list[0] == OWL.intersectionOf:
            return Conjunction(arguments=formulas)
        if typed_list[0] == OWL.complementOf:
            return Negation(arguments=formulas)
    
    logging.warning(msg='Something is wrong with the list: ' + str(typed_list))

def get_subformula_from_uri(uri: URIRef, owl_ontology: Graph, variable=Variable()) -> Formula:
    if (uri, RDF.type, OWL.Class) in owl_ontology:
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin=uri, arity=1)
        return \
            AtomicFormula(predicate=predicate, arguments=[variable])
    
    if uri == OWL.NamedIndividual:
        predicate = Predicate.registry[uri]
        return \
            AtomicFormula(predicate=predicate, arguments=[variable])
    
    if uri_is_property(uri=uri, owl_ontology=owl_ontology):
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin=uri, arity=2)
        return \
            AtomicFormula(predicate=predicate, arguments=[Variable(letter=TPTP_DEFAULT_LETTER_1), Variable(letter=TPTP_DEFAULT_LETTER_2)])
    
    logging.warning(msg='Cannot get formula from ' + str(uri))
    

def get_fol_symbol_for_owl_node(node: Node, owl_ontology: Graph, arity=1) -> Symbol:
    if (node, RDF.type, OWL.NamedIndividual) in owl_ontology or (node, RDF.type, RDFS.Literal) in owl_ontology:
        if node in Term.registry:
            return Term.registry[node]
        else:
            return Term(origin=node)
    
    if node in Predicate.registry:
        return Predicate.registry[node]
    else:
        return Predicate(origin=node, arity=arity)


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
    
    if len(owl_someValuesFrom) > 0:
        restricting_node = owl_someValuesFrom[0]
        restricting_class_formula = get_simple_subformula_from_node(node=restricting_node, owl_ontology=owl_ontology, variable=Variable(letter=TPTP_DEFAULT_LETTER_2))
        restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Conjunction(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.EXISTENTIAL,
                    variables=[Variable(letter=TPTP_DEFAULT_LETTER_2)])
            return formula
    
    if len(owl_allValuesFrom) > 0:
        restricting_node = owl_allValuesFrom[0]
        restricting_class_formula = get_simple_subformula_from_node(node=restricting_node, owl_ontology=owl_ontology, variable=Variable(letter=TPTP_DEFAULT_LETTER_2))
        restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Implication(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.UNIVERSAL,
                    variables=[Variable(letter=TPTP_DEFAULT_LETTER_2)])
            return formula
        
    if len(owl_onClass) > 0 or len(owl_onDataRange) > 0:
        if len(owl_onClass) > 0:
            restricting_node = owl_onClass[0]
        else:
            restricting_node = owl_onDataRange[0]
        restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
        if restricting_relation_formula:
            if len(owl_qualifiedMinCardinality) > 0:
                minCardinality = int(owl_qualifiedMinCardinality[0])
                if minCardinality == 0:
                    return None
                conjunction = None
                variables = list()
                index = 1
                while index <= minCardinality + 1:
                    variable = Variable(letter=TPTP_DEFAULT_LETTER_2 + str(index))
                    restricting_class_formula = get_simple_subformula_from_node(node=restricting_node, owl_ontology=owl_ontology, variable=variable)
                    
                    # restricting_relation_formula = get_subformula_from_node(node=owl_property,owl_ontology=owl_ontology,variable=DefaultVariable(letter=TPTP_DEFAULT_LETTER_1 + str(index)))
                    if not conjunction:
                        conjunction = restricting_relation_formula
                    else:
                        conjunction = Conjunction(arguments=[conjunction, restricting_class_formula])
                        for backward_index in range(1,index):
                            conjunction = Conjunction(arguments=[conjunction, IdentityFormula(arguments=[variables[-1], variable])])
                    variables.append(variable)
                    index += 1
                formula = \
                    QuantifyingFormula(
                        quantified_formula=Conjunction(arguments=[restricting_relation_formula, conjunction]),
                        quantifier=Quantifier.EXISTENTIAL,
                        variables=[Variable(letter=TPTP_DEFAULT_LETTER_2)])
                return formula
            
    if len(owl_hasValue) > 0:
        restricting_relation_symbol = get_fol_symbol_for_owl_node(node=owl_property, owl_ontology=owl_ontology)
        restricting_individual_symbol = get_fol_symbol_for_owl_node(node=owl_hasValue[0], owl_ontology=owl_ontology)
        formula = AtomicFormula(predicate=restricting_relation_symbol, arguments=[variable, restricting_individual_symbol])
        return formula
    
    logging.warning(msg='Cannot get formula from a restriction')


def uri_is_property(uri: Node, owl_ontology: Graph) -> bool:
    if (uri, RDF.type, OWL.ObjectProperty) in owl_ontology:
        return True
    if (uri, RDF.type, OWL.DatatypeProperty) in owl_ontology:
        return True
    if (uri, RDF.type, RDF.Property) in owl_ontology:
        return True
    return False


def try_to_cast_bnode_as_typed_list(bnode: BNode, owl_ontology: Graph) -> tuple:
    owl_unions = list(owl_ontology.objects(subject=bnode, predicate=OWL.unionOf))
    if len(owl_unions) > 0:
        return OWL.unionOf, owl_unions[0]
    
    owl_intersections = list(owl_ontology.objects(subject=bnode, predicate=OWL.intersectionOf))
    if len(owl_intersections) > 0:
        return OWL.intersectionOf, owl_intersections[0]
    
    owl_complements = list(owl_ontology.objects(subject=bnode, predicate=OWL.complementOf))
    if len(owl_complements) > 0:
        return OWL.complementOf, owl_complements[0]
    
    # return \
    #     OWL.propertyChainAxiom, list(owl_ontology.objects(subject=bnode, predicate=OWL.propertyChainAxiom))
    # v=0


def get_listed_resources(rdf_list_object: Resource, ontology: Graph, rdf_list: list) -> list:
    first_items_in_rdf_list = list(ontology.objects(subject=rdf_list_object, predicate=RDF.first))
    if len(first_items_in_rdf_list) == 0:
        return rdf_list
    resource = get_simple_subformula_from_node(node=first_items_in_rdf_list[0], owl_ontology=ontology)
    rdf_list.append(resource)
    rest_items_in_rdf_list = list(ontology.objects(subject=rdf_list_object, predicate=RDF.rest))
    rdf_list = get_listed_resources(rdf_list_object=rest_items_in_rdf_list[0], ontology=ontology, rdf_list=rdf_list)
    return rdf_list