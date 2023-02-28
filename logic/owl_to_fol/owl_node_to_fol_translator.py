from rdflib import Graph, OWL, RDF, RDFS
from rdflib.term import Node, BNode, URIRef

from logic.owl_to_fol.objects.atomic_formula import AtomicFormula
from logic.owl_to_fol.objects.conjunction import Conjunction
from logic.owl_to_fol.objects.default_variable import DefaultVariable, TPTP_DEFAULT_LETTER_1, TPTP_DEFAULT_LETTER_2
from logic.owl_to_fol.objects.disjunction import Disjunction
from logic.owl_to_fol.objects.formula import Formula
from logic.owl_to_fol.objects.identity_formula import IdentityFormula
from logic.owl_to_fol.objects.implication import Implication
from logic.owl_to_fol.objects.negation import Negation
from logic.owl_to_fol.objects.predicate import Predicate
from logic.owl_to_fol.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.owl_to_fol.objects.symbol import Symbol
from logic.owl_to_fol.objects.term import Term
from logic.owl_to_fol.owl_helpers import uri_is_property, try_to_cast_bnode_as_typed_list, get_listed_resources
from logic.owl_to_fol.owl_to_fol_preparer import populate_default_predicates


def get_simple_subformula_from_node(node: Node, owl_ontology: Graph, variable=DefaultVariable()) -> Formula:
    if isinstance(node, BNode):
        return get_subformula_from_bnode(bnode=node, owl_ontology=owl_ontology, variable=variable)
    if isinstance(node, URIRef):
       return get_subformula_from_uri(uri=node, owl_ontology=owl_ontology, variable=variable)


def get_subformula_from_bnode(bnode: BNode, owl_ontology: Graph, variable=DefaultVariable()) -> Formula:
    if (bnode, RDF.type, OWL.Restriction) in owl_ontology:
        formula = generate_fol_from_owl_restriction(owl_restriction=bnode, owl_ontology=owl_ontology)
        return formula
    
    if len(list(owl_ontology.objects(subject=bnode, predicate=OWL.inverseOf))) > 0:
        if bnode in Predicate.registry:
            predicate = Predicate.registry[bnode]
        else:
            predicate = Predicate(origin=bnode, arity=2)
        return \
            AtomicFormula(predicate=predicate, arguments=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_2),DefaultVariable(letter=TPTP_DEFAULT_LETTER_1)])

    typed_list = try_to_cast_bnode_as_typed_list(bnode=bnode, owl_ontology=owl_ontology)
    
    if typed_list:
        if typed_list[0] == OWL.complementOf:
            listed_resources = [typed_list[1]]
        else:
            listed_resources = get_listed_resources(rdf_list_object=typed_list[1],ontology=owl_ontology,rdf_list=list())
        formulas = list()
        for listed_resource in listed_resources:
            formula = get_simple_subformula_from_node(node=listed_resource, owl_ontology=owl_ontology, variable=variable)
            formulas.append(formula)
        if typed_list[0] == OWL.unionOf:
            return Disjunction(arguments=formulas)
        if typed_list[0] == OWL.intersectionOf:
            return Conjunction(arguments=formulas)
        if typed_list[0] == OWL.complementOf:
            return Negation(arguments=formulas)
        
    v=0

def get_subformula_from_uri(uri: URIRef, owl_ontology: Graph, variable=DefaultVariable()) -> Formula:
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
            AtomicFormula(predicate=predicate, arguments=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_1),DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)])
    
    v=0
    

def get_fol_object_for_node(node: Node, owl_ontology: Graph, arity=1) -> Symbol:
    if (node, RDF.type, OWL.NamedIndividual) in owl_ontology or (node, RDF.type, RDFS.Literal) in owl_ontology:
        if node in Term.registry:
            return Term.registry[node]
        else:
            return Term(origin=node)
    
    if node in Predicate.registry:
        return Predicate.registry[node]
    else:
        return Predicate(origin=node, arity=arity)


def generate_fol_from_owl_restriction(owl_restriction: Node, owl_ontology: Graph) -> Formula:
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
        restricting_class_formula = get_simple_subformula_from_node(node=restricting_node, owl_ontology=owl_ontology, variable=DefaultVariable(letter=TPTP_DEFAULT_LETTER_2))
        restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Conjunction(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.EXISTENTIAL,
                    variables=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)])
            return formula
    
    if len(owl_allValuesFrom) > 0:
        restricting_node = owl_allValuesFrom[0]
        restricting_class_formula = get_simple_subformula_from_node(node=restricting_node, owl_ontology=owl_ontology, variable=DefaultVariable(letter=TPTP_DEFAULT_LETTER_2))
        restricting_relation_formula = get_simple_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
        if restricting_class_formula and restricting_relation_formula:
            formula = \
                QuantifyingFormula(
                    quantified_formula=Implication(arguments=[restricting_relation_formula, restricting_class_formula]),
                    quantifier=Quantifier.UNIVERSAL,
                    variables=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)])
            return formula
        
    if len(owl_onClass) > 0:
        restricting_node = owl_onClass[0]
        # restricting_class_formula = get_subformula_from_node(node=restricting_node, owl_ontology=owl_ontology, variable=DefaultVariable(letter=TPTP_DEFAULT_LETTER_2))
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
                    variable = DefaultVariable(letter=TPTP_DEFAULT_LETTER_2 + str(index))
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
                        variables=[DefaultVariable(letter=TPTP_DEFAULT_LETTER_2)])
                return formula