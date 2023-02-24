from rdflib import Graph, OWL, RDF, RDFS
from rdflib.term import Node, BNode

from logic.owl_to_fol.objects.atomic_formula import AtomicFormula
from logic.owl_to_fol.objects.conjunction import Conjunction
from logic.owl_to_fol.objects.default_variable import DefaultVariable
from logic.owl_to_fol.objects.formula import Formula
from logic.owl_to_fol.objects.identity_formula import IdentityFormula
from logic.owl_to_fol.objects.implication import Implication
from logic.owl_to_fol.objects.negation import Negation
from logic.owl_to_fol.objects.predicate import Predicate
from logic.owl_to_fol.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.owl_to_fol.objects.symbol import Symbol
from logic.owl_to_fol.objects.term import Term
from logic.owl_to_fol.owl_to_fol_preparer import populate_default_predicates

def get_subformula_from_node(node: Node, owl_ontology: Graph, variable=DefaultVariable()) -> Formula:
    if (node, RDF.type, OWL.Class) in owl_ontology:
        if node in Predicate.registry:
            predicate = Predicate.registry[node]
        else:
            predicate = Predicate(origin=node, arity=1)
        return AtomicFormula(predicate=predicate, arguments=[variable])
    if (node, RDF.type, OWL.Restriction) in owl_ontology:
        formula = generate_fol_from_owl_restriction(owl_restriction=node, owl_ontology=owl_ontology)
        return formula
    return None


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
        if isinstance(restricting_node, BNode):
            return None
        restricting_class_formula = get_subformula_from_node(node=restricting_node,owl_ontology=owl_ontology)
        restricting_relation_formula = get_subformula_from_node(node=owl_property, owl_ontology=owl_ontology)
        formula = \
            QuantifyingFormula(
                quantified_formula=Conjunction(arguments=[restricting_relation_formula, restricting_class_formula]),
                quantifier=Quantifier.EXISTENTIAL,
                variables=[DefaultVariable()])
        return formula