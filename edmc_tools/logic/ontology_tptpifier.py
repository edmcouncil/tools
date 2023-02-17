import logging

from rdflib import Graph, URIRef

from logic.ply_parser import parse_formula_infix_notation

def preprocess_axiom(axiom: str) -> str:
    if ':' not in axiom:
        return axiom
    prefix_index = axiom.index(':') + 1
    return axiom[prefix_index:]

def tptpify(axiom_annotatation_properties: set, ontology: Graph) -> str:
    tptpified_ontology = str()
    for axiom_annotatation_property in axiom_annotatation_properties:
        logical_annotations = list(ontology.subject_objects(predicate=URIRef(axiom_annotatation_property)))
        for logical_annotation in logical_annotations:
            axiom = str(logical_annotation[1])
            preprocessed_axiom = preprocess_axiom(axiom=axiom)
            formula = parse_formula_infix_notation(text=preprocessed_axiom)
            if not formula == None:
                tptpified_ontology += '\n' + formula.to_tptp()
    return tptpified_ontology
    
            
iof_ontology = Graph()
iof_ontology.parse('../resources/iof/dev.iof-quickstart.ttl')

iof_axiom_properties = \
    {
        'https://spec.industrialontologies.org/ontology/core/meta/AnnotationVocabulary/firstOrderLogicAxiom',
        'https://spec.industrialontologies.org/ontology/core/meta/AnnotationVocabulary/firstOrderLogicDefinition'
    }

logging.basicConfig(format='%(message)s', level=logging.INFO,datefmt='%m/%d/%Y %I:%M:%S %p', filename='iof_axioms.log')

tptpified_ontology = tptpify(axiom_annotatation_properties=iof_axiom_properties,ontology=iof_ontology)
print(tptpified_ontology)