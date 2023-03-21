import logging

from rdflib import Graph, OWL, RDF, RDFS

from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.filterers.translation_filterer import node_is_out_of_scope, triple_is_of_of_scope
from logic.owl_to_fol.translators.owl_class_like_translator import translate_rdf_triple_about_class_like_to_fol
from logic.owl_to_fol.translators.owl_individual_translator import translate_rdf_triple_about_individual_subject_to_fol
from logic.owl_to_fol.translators.owl_node_to_fol_translator import translate_all_different_triple
from logic.owl_to_fol.translators.owl_property_translator import translate_rdf_triple_about_property_to_fol
from logic.owl_to_fol.translators.translator_helpers import __can_uri_be_cast_to_binary_predicate


def translate_rdf_triple_to_fol(rdf_triple: tuple, owl_ontology: Graph):
    Variable.clear_used_variable_letters()
    
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
    
    rdf_triple_is_out_of_scope = triple_is_of_of_scope(rdf_triple=rdf_triple)
    if rdf_triple_is_out_of_scope:
        logging.info('Dropping an out-of scope triple ' + str(rdf_triple))
        return
    
    if (rdf_triple_subject, RDF.type, OWL.NamedIndividual) in owl_ontology:
        translate_rdf_triple_about_individual_subject_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
        return
    
    if (rdf_triple_subject, RDF.type, OWL.Class) in owl_ontology or (rdf_triple_subject, RDF.type, OWL.Restriction) in owl_ontology or (rdf_triple_subject, RDF.type, RDFS.Datatype) in owl_ontology:
        translate_rdf_triple_about_class_like_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
        return
        
    if rdf_triple_predicate == OWL.distinctMembers:
        translate_all_different_triple(differents_node=rdf_triple_object, owl_ontology=owl_ontology)
        return
        
    if __can_uri_be_cast_to_binary_predicate(uri=rdf_triple_subject, owl_ontology=owl_ontology):
        translate_rdf_triple_about_property_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
        return
    
    logging.warning(msg='Cannot migrate ' + str(rdf_triple))

