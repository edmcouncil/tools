import spacy
from rdflib import Graph, OWL, URIRef, RDF, SKOS

SPACY_MODEL_NAME = 'en_core_web_trf'
DETERMINER = 'The'
VERB = 'means'
OBJECT = 'nothing'
SEPARATOR = ' '
PUNCTUATION = '.'


def check_ontology_annotations(ontology_file_path: str):
    ontology = Graph()
    nlp = spacy.load(SPACY_MODEL_NAME)
    ontology.parse(ontology_file_path)
    class_labels = __get_phrases_from_annotation_property(ontology=ontology, annotation_property=SKOS.definition, type_uri=OWL.Class)
    suspicious_class_labels = __check_phrases(phrases=class_labels, acceptable_parts_of_speech=['NP', 'NOUN', 'NNP', 'PROPN', 'PRON'], nlp=nlp)
    list(suspicious_class_labels).sort()
    for suspicious_class, suspicious_class_label in suspicious_class_labels.items():
        print(suspicious_class, '\t', suspicious_class_label)


def __check_phrases(phrases: dict, acceptable_parts_of_speech: list, nlp) -> dict:
    suspicious_phrases = dict()
    for resource, phrase in phrases.items():
        phrase_under_consideration = phrase
        phrase_root = None
        if phrase_under_consideration.startswith('a '):
            phrase_under_consideration = DETERMINER + SEPARATOR + phrase_under_consideration[2:]
        if phrase_under_consideration.startswith('an '):
            phrase_under_consideration = DETERMINER + SEPARATOR + phrase_under_consideration[3:]
        if not phrase_under_consideration.startswith('The ') and not phrase_under_consideration.startswith('the '):
            phrase_under_consideration = DETERMINER + SEPARATOR + phrase_under_consideration
        if phrase_under_consideration.endswith(PUNCTUATION):
            phrase_under_consideration = phrase_under_consideration[:-1]
        parsed_phrase = phrase_under_consideration + SEPARATOR + VERB + SEPARATOR + OBJECT + PUNCTUATION
        spacy_tokens_in_phrase = nlp(parsed_phrase)
        for spacy_token in spacy_tokens_in_phrase:
            if spacy_token.dep_ == 'ROOT':
                if spacy_token.text == VERB:
                    phrase_root = spacy_token
        if phrase_root is not None:
            root_children = phrase_root.children
            is_phrase_suspicious = True
            for root_child in root_children:
                if not root_child.text == DETERMINER and not root_child.text == OBJECT and not root_child.text == PUNCTUATION:
                    if root_child.pos_ in acceptable_parts_of_speech:
                        is_phrase_suspicious = False
                        break
            if is_phrase_suspicious:
                suspicious_phrases[resource] = phrase
    return suspicious_phrases


def __get_phrases_from_annotation_property(ontology: Graph, annotation_property: OWL.AnnotationProperty, type_uri: URIRef) -> dict:
    phrases = dict()
    for (subject, property, object) in ontology:
        if property == annotation_property:
            if (subject, RDF.type, type_uri) in ontology:
                phrases[subject] = object.value
    return phrases


check_ontology_annotations('https://spec.pistoiaalliance.org/idmp/ontology/master/latest/QuickIDMPDev.ttl')
