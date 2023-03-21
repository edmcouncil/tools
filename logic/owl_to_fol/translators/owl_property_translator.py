import logging

from rdflib import Graph, RDF, OWL, RDFS

from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.equivalence import Equivalence
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.translators.owl_node_to_fol_translator import get_simple_subformula_from_node


def translate_rdf_triple_about_property_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    first_variable = Variable(letter=Variable.get_next_variable_letter())
    second_variable = Variable(letter=Variable.get_next_variable_letter())
    third_variable = Variable(letter=Variable.get_next_variable_letter())
    if rdf_triple[1] == RDF.type:
        if rdf_triple[2] == OWL.TransitiveProperty:
            property_formula_1 = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology, variables=[first_variable, second_variable])
            property_formula_2 = property_formula_1.replace_arguments(arguments=[second_variable, third_variable])
            property_formula_3 = property_formula_1.replace_arguments(arguments=[first_variable, third_variable])
            quantifying_variables = [first_variable, second_variable, third_variable]
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[Conjunction(arguments=[property_formula_1, property_formula_2]), property_formula_3]),
                variables=quantifying_variables,
                quantifier=Quantifier.UNIVERSAL,
                is_self_standing=True)
            return
        if rdf_triple[2] == OWL.FunctionalProperty:
            property_formula_1 = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology, variables=[first_variable, second_variable])
            property_formula_2 = property_formula_1.replace_arguments(arguments=[first_variable, third_variable])
            identity_formula = IdentityFormula(arguments=[second_variable, third_variable])
            quantifying_variables = [first_variable, second_variable, third_variable]
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[Conjunction(arguments=[property_formula_1, property_formula_2]), identity_formula]),
                variables=quantifying_variables,
                quantifier=Quantifier.UNIVERSAL,
                is_self_standing=True)
            return
        if rdf_triple[2] == OWL.InverseFunctionalProperty:
            property_formula_1 = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology, variables=[first_variable, second_variable])
            property_formula_2 = property_formula_1.replace_arguments(arguments=[third_variable, second_variable])
            identity_formula = IdentityFormula(arguments=[first_variable, third_variable])
            quantifying_variables = [first_variable, second_variable, third_variable]
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[Conjunction(arguments=[property_formula_1, property_formula_2]), identity_formula]),
                variables=quantifying_variables,
                quantifier=Quantifier.UNIVERSAL,
                is_self_standing=True)
            return
        if rdf_triple[2] == OWL.SymmetricProperty:
            property_formula_1 = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology, variables=[first_variable, second_variable])
            property_formula_2 = property_formula_1.replace_arguments(arguments=[second_variable, first_variable])
            quantifying_variables = [first_variable, second_variable]
            QuantifyingFormula(
                quantified_formula=Implication(arguments=[property_formula_1, property_formula_2]),
                variables=quantifying_variables,
                quantifier=Quantifier.UNIVERSAL,
                is_self_standing=True)
            return
    antecedent = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology, variables=[first_variable, second_variable])
    subsequent = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology, variables=[first_variable, second_variable])
    if not antecedent:
        logging.warning(msg='Cannot process property statement: ' + str(rdf_triple) + ' because of antecedent')
        return
    if not subsequent:
        logging.warning(msg='Cannot process property statement: ' + str(rdf_triple) + ' because of subsequent')
        return
    
    if rdf_triple[1] == RDFS.subPropertyOf:
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[antecedent, subsequent]),
            variables=[first_variable, second_variable],
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
        return
    
    if rdf_triple[1] == OWL.equivalentProperty:
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[antecedent, subsequent]),
            variables=[first_variable, second_variable],
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
        return
    
    if rdf_triple[1] == OWL.propertyDisjointWith:
        overlap_formula = \
            QuantifyingFormula(
                quantified_formula=Conjunction(arguments=[antecedent, subsequent]),
                variables=[first_variable, second_variable],
                quantifier=Quantifier.EXISTENTIAL)
        Negation(arguments=[overlap_formula], is_self_standing=True)
        
        return
    
    if rdf_triple[1] == OWL.propertyChainAxiom:
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[subsequent, antecedent]),
            variables=[first_variable, second_variable],
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
        return
    
    if rdf_triple[1] == RDFS.domain:
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[antecedent, subsequent]),
            variables=[first_variable, second_variable],
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
        return
    
    if rdf_triple[1] == RDFS.range:
        subsequent = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology, variables=[second_variable])
        QuantifyingFormula(
            quantified_formula=Implication(arguments=[antecedent, subsequent]),
            variables=[first_variable, second_variable],
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
        return
    
    if rdf_triple[1] == OWL.inverseOf:
        subsequent = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology, variables=[first_variable, second_variable])
        if not antecedent is None and not subsequent is None:
            subsequent.swap_arguments(inplace=True)
            QuantifyingFormula(
                quantified_formula=Equivalence(arguments=[antecedent, subsequent]),
                variables=[first_variable, second_variable],
                quantifier=Quantifier.UNIVERSAL,
                is_self_standing=True)
        else:
            logging.warning(msg='Cannot process inverse property statement: ' + str(rdf_triple))
        return
    
    logging.warning(msg='Cannot process property statement: ' + str(rdf_triple))
