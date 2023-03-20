import logging

from rdflib import Graph, OWL, RDF, RDFS

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.equivalence import Equivalence
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.implication import Implication
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.filterers.translation_filterer import node_is_out_of_scope, triple_is_of_of_scope
from logic.owl_to_fol.translators.owl_node_to_fol_translator import get_simple_subformula_from_node
from logic.owl_to_fol.translators.translator_helpers import get_fol_symbol_for_owl_node, \
    __can_uri_be_cast_to_binary_predicate


def translate_rdf_triple_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    rdf_triple_subject = rdf_triple[0]
    rdf_triple_predicate = rdf_triple[1]
    rdf_triple_object = rdf_triple[2]
    
    rdf_triple_subject_is_out_of_scope = node_is_out_of_scope(node=rdf_triple_subject, owl_ontology=owl_ontology)
    if rdf_triple_subject_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(rdf_triple_subject) + ' as the subject')
        return
    
    rdf_triple_predicate_is_out_of_scope = node_is_out_of_scope(node=rdf_triple_predicate, owl_ontology=owl_ontology)
    if rdf_triple_predicate_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(rdf_triple_predicate) + ' as the predicate')
        return
    
    rdf_triple_object_is_out_of_scope = node_is_out_of_scope(node=rdf_triple_object, owl_ontology=owl_ontology)
    if rdf_triple_object_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(rdf_triple_object) + ' as the object')
        return
    
    rdf_triple_object_is_out_of_scope = triple_is_of_of_scope(rdf_triple=rdf_triple)
    if rdf_triple_object_is_out_of_scope:
        logging.info('Dropping a out-of scope triple ' + str(rdf_triple))
        return
    
    rdf_triple = (rdf_triple_subject, rdf_triple_predicate, rdf_triple_object)
    
    if (rdf_triple_subject, RDF.type, OWL.NamedIndividual) in owl_ontology:
        translate_rdf_triple_about_individual_subject_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
        Variable.clear_used_variable_letters()
        return
    
    if (rdf_triple_subject, RDF.type, OWL.Class) in owl_ontology or (rdf_triple_subject, RDF.type, OWL.Restriction) in owl_ontology:
        translate_rdf_triple_about_class_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
        Variable.clear_used_variable_letters()
        return
        
    if __can_uri_be_cast_to_binary_predicate(uri=rdf_triple_subject, owl_ontology=owl_ontology):
        translate_rdf_triple_about_property_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
        Variable.clear_used_variable_letters()
        return


def translate_rdf_triple_about_individual_subject_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    Variable.clear_used_variable_letters()
    triple_subject = get_fol_symbol_for_owl_node(node=rdf_triple[0], owl_ontology=owl_ontology)
    triple_predicate = get_fol_symbol_for_owl_node(node=rdf_triple[1], owl_ontology=owl_ontology, arity=2)
    triple_object = get_fol_symbol_for_owl_node(node=rdf_triple[2], owl_ontology=owl_ontology)
    if rdf_triple[1] == RDF.type:
        get_simple_subformula_from_node(node=rdf_triple[2], variables=[triple_subject], owl_ontology=owl_ontology)
        return
    if rdf_triple[1] == OWL.sameAs:
        IdentityFormula(arguments=[triple_subject, triple_object])
        return
    if rdf_triple[1] == OWL.differentFrom:
        Negation(arguments=[IdentityFormula(arguments=[triple_subject, triple_object])])
        return
    AtomicFormula(predicate=triple_predicate, arguments=[triple_subject, triple_object], is_self_standing=True)


def translate_rdf_triple_about_class_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    Variable.clear_used_variable_letters()
    variable = Variable(letter=Variable.get_next_variable_letter())
    # second_variable = Variable(letter=Variable.get_next_variable_letter())
    left_class = get_simple_subformula_from_node(node=rdf_triple[0], owl_ontology=owl_ontology, variables=[variable])
    right_class = get_simple_subformula_from_node(node=rdf_triple[2], owl_ontology=owl_ontology, variables=[variable])
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
    
    if rdf_triple[1] == OWL.disjointUnionOf:
        logging.warning(msg='owl:disjointUnionOf not yet implemented')
        return
        # QuantifyingFormula(
        #     quantified_formula=Equivalence(arguments=[left_class, right_class]),
        #     variables=[Variable()],
        #     quantifier=Quantifier.UNIVERSAL)
        # return

    if (rdf_triple[0], RDF.type, OWL.Restriction) not in owl_ontology:
        logging.warning(msg='Cannot process class statement: ' + str(rdf_triple))
 
    
def translate_rdf_triple_about_property_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    Variable.clear_used_variable_letters()
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