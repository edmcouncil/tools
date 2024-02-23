import logging

from rdflib import Graph, URIRef

from logic.fol_logic.iof_ply_parser import parse_formula_infix_notation


def preprocess_axiom(axiom: str) -> str:
    if ':' not in axiom:
        return axiom
    prefix_index = axiom.index(':') + 1
    return axiom[prefix_index:]

def check_axioms_in_annotations(axiom_annotatation_properties: set, ontology: Graph):
    for axiom_annotatation_property in axiom_annotatation_properties:
        logical_annotations = list(ontology.subject_objects(predicate=URIRef(axiom_annotatation_property)))
        for logical_annotation in logical_annotations:
            axiom = str(logical_annotation[1])
            preprocessed_axiom = preprocess_axiom(axiom=axiom)
            one_line_axiom = axiom.replace('\n',' ')
            resource = str(logical_annotation[0])
            if not preprocessed_axiom.count('(') == preprocessed_axiom.count(')'):
                logging.warning(msg='|'.join(['unbalanced brackets', resource, one_line_axiom]))
                continue
            parsed_axiom = parse_formula_infix_notation(text=preprocessed_axiom)
            if parsed_axiom == None:
                logging.warning(msg='|'.join(['ill-formed', resource, one_line_axiom]))
            
iof_ontology = Graph()
iof_ontology.parse('/Users/pawel.garbacz/iof/core/Core.rdf')

iof_axiom_properties = \
    {
        'https://spec.industrialontologies.org/ontology/core/meta/AnnotationVocabulary/firstOrderLogicAxiom',
        'https://spec.industrialontologies.org/ontology/core/meta/AnnotationVocabulary/firstOrderLogicDefinition'
    }

logging.basicConfig(format='%(message)s', level=logging.INFO,datefmt='%m/%d/%Y %I:%M:%S %p', filename='iof_axioms.log')

check_axioms_in_annotations(axiom_annotatation_properties=iof_axiom_properties,ontology=iof_ontology)