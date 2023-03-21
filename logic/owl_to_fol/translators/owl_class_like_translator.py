import logging

from rdflib import Graph, RDFS, OWL

from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.equivalence import Equivalence
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.owl_node_to_fol_translator import get_simple_subformula_from_node, \
    translate_all_disjoint_classes_triple


def translate_rdf_triple_about_class_like_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    variable = Variable(letter=Variable.get_next_variable_letter())
    left_class = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology, variables=[variable])
    right_class = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology, variables=[variable])

    if rdf_triple[1] == OWL.disjointUnionOf:
        logging.warning(msg='owl:disjointUnionOf not yet implemented')
        return

    if rdf_triple[1] == OWL.members or rdf_triple[2] == OWL.AllDisjointClasses:
        translate_all_disjoint_classes_triple(all_disjoint_classes_node=rdf_triple[0], owl_ontology=owl_ontology,
                                              variable=variable)
        return
    
    if not left_class:
        logging.warning(msg='Cannot process class statement: ' + str(rdf_triple))
        return
    if not right_class:
        logging.warning(msg='Cannot process class statement: ' + str(rdf_triple))
        return
        
    if rdf_triple[1] == RDFS.subClassOf:
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[left_class, right_class]),
            variables=[Variable()],
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
        return
    
    if rdf_triple[1] == OWL.equivalentClass:
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[left_class, right_class]),
            variables=[Variable()],
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
        return
    
    if rdf_triple[1] == OWL.complementOf:
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[Negation([left_class]), right_class]),
            variables=[Variable()],
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
        return
    
    if rdf_triple[1] == OWL.disjointWith:
        overlap_formula = \
            QuantifyingFormula(
                quantified_formula=Conjunction(arguments=[left_class, right_class]),
                variables=[Variable()],
                quantifier=Quantifier.EXISTENTIAL)
        Negation(arguments=[overlap_formula], is_self_standing=True)
        return
    
    
        
    logging.warning(msg='Cannot process class statement: ' + str(rdf_triple))
