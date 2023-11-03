from docx import Document as WordDocument
from rdflib import Graph, Literal
import spacy
from spacy import Language
from spacy.matcher import PhraseMatcher, Matcher
from spacy.tokens import Doc
from tqdm import tqdm

nlp = spacy.load("en_core_web_sm")
matcher = Matcher(nlp.vocab)

# def __text_matches_document(doc: Doc, text: str):
#     phrase_pattern = [{'TEXT': {"FUZZY": text}}]
#     patterns = [phrase_pattern]
#     matcher.add("Text", patterns)
#     matches = matcher(doc)
#     matcher.remove("Text")
#     if len(matches) > 0:
#         # for match_id, start, end in matches:
#         #     span = doc[start:end]
#         #     print(span.text)
#         return True
#     else:
#         return False
    


def annotate_docx_document_with_ontology(docx_document_path: str, ontology_location: str, annotated_docx_document_path: str):
    document = WordDocument(docx_document_path)
    paragraphs = document.paragraphs
    text = str()
    for paragraph in paragraphs:
        text += paragraph.text
    text_doc = nlp(text)
    text_length = len(text)
    
    matched_text = str()
    ontology = Graph()
    ontology.parse(ontology_location)
    
    pattern_phrases = set()
    for (triple_subject, triple_predicate, triple_object) in ontology:
        if isinstance(triple_object, Literal):
            literal_value = triple_object.value
            if isinstance(literal_value, str):
                if literal_value in text:
                    matched_text += literal_value
                elif not all(char.isdigit() for char in literal_value) and len(literal_value) > 7:
                    pattern_phrases.add(literal_value)
    patterns = list()
    for pattern_phrase in pattern_phrases:
        pattern = [{'TEXT': {"FUZZY": pattern_phrase}}]
        patterns.append(pattern)
    matcher.add("Phrases", patterns)
    matches = matcher(text_doc)
    for match_id, start, end in matches:
        span = text_doc[start:end]
        matched_text += span.text

    matched_text_length = len(matched_text)
    
    print(text_length)
    print(matched_text_length)
    print(str(matched_text_length/text_length))
    
    
annotate_docx_document_with_ontology(
    docx_document_path='/Users/pawel.garbacz/Library/CloudStorage/OneDrive-MakoLabS.A/idmp/ISO Standards/ISO_11616_2017(en).docx',
    ontology_location='https://spec.pistoiaalliance.org/idmp/ontology/master/latest/QuickIDMPDev.ttl',
    annotated_docx_document_path='/Users/pawel.garbacz/Library/CloudStorage/OneDrive-MakoLabS.A/idmp/ISO Standards/ISO_11616_2017(en)_annotated.docx')
    