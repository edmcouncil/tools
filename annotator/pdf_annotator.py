import sys

import fitz
from fitz import Rect, Page, TEXTFLAGS_WORDS, TEXT_PRESERVE_WHITESPACE
from rdflib import Literal, Graph, RDFS, URIRef
from tqdm import tqdm


ANNOTATION_PROPERTIES_IN_SCOPE = \
    {
        RDFS.label,
        URIRef('https://www.omg.org/spec/Commons/AnnotationVocabulary/acronym'),
        URIRef('https://www.omg.org/spec/Commons/AnnotationVocabulary/synonym')
    }

WORD_SEPARATORS = [',', '.', ';']


def __rect1_intersects_rect2(rect1: Rect, rect2: Rect) -> bool:
    # rect1_normalized = rect1.normalize()
    # rect2_normalized = rect2.normalize()
    if not rect1.intersects(rect2):
        return False
    if not rect1.tl.y == rect2.tl.y or not rect1.br.y == rect2.br.y:
        return False
    return True



def __rect_is_already_annotated(rect: Rect, annotated_rects: set) -> bool:
    for annotated_rect in annotated_rects:
        if __rect1_intersects_rect2(rect1=annotated_rect, rect2=rect):
            return True
    return False


def __get_all_annotating_value_variants(annotating_value: str) -> set:
    pluralised_annotating_values = {annotating_value}
    if annotating_value[-1] == 's':
        pluralised_annotating_values.add(annotating_value + 'es')
    else:
        pluralised_annotating_values.add(annotating_value + 's')
    if len(annotating_value) > 16:
        return pluralised_annotating_values
    
    extended_annotating_values = set()
    for pluralised_annotating_value in pluralised_annotating_values:
        extended_annotating_values.add(' ' + pluralised_annotating_value + ' ')
        for word_separator in WORD_SEPARATORS:
            extended_annotating_values.add(word_separator + ' ' + pluralised_annotating_value + ' ')
            extended_annotating_values.add(' ' + pluralised_annotating_value + word_separator)
            extended_annotating_values.add(word_separator + ' ' + pluralised_annotating_value + word_separator)
    return extended_annotating_values


def __add_annotation_from_text_to_page(
        page: Page,
        annotated_rects: set,
        annotating_resource: str,
        rects: set,
        annotating_value: str):
    for rect in rects:
        rect_normalised = rect.normalize()
        if not __rect_is_already_annotated(rect=rect_normalised, annotated_rects=annotated_rects):
            page.add_text_annot(point=rect_normalised.bl, text=str(annotating_value + ' | ' + str(annotating_resource)), icon='Tag')
            page.add_highlight_annot(rect_normalised.quad)
            annotated_rects.add(rect_normalised)


def __add_annotation_to_page(annotating_value: str, page: Page, annotated_rects: set, annotating_resource: str):
    words = page.get_text('words')
    rects = page.search_for(annotating_value, flags=TEXT_PRESERVE_WHITESPACE)
    __add_annotation_from_text_to_page(
        page=page,
        annotated_rects=annotated_rects,
        annotating_resource=annotating_resource,
        rects=rects, annotating_value=annotating_value)
    

def annotate_pdf_document_with_ontology(document_path: str, ontology_location: str, annotated_document_path: str, filter: str):
    ontology = Graph()
    ontology.parse(ontology_location)
    annotations = dict()
    for (triple_subject, triple_predicate, triple_object) in ontology:
        if filter in str(triple_subject):
            if triple_predicate in ANNOTATION_PROPERTIES_IN_SCOPE:
                if isinstance(triple_object, Literal):
                    literal_value = triple_object.value
                    if isinstance(literal_value, str):
                        if not all(char.isdigit() for char in literal_value) and len(literal_value) > 3:
                            annotations[literal_value] = triple_subject
    
    extended_annotations = dict()
    for annotating_value, annotated_resource in annotations.items():
        # annotating_value_variants = __get_all_annotating_value_variants(annotating_value=annotating_value)
        annotating_value_variants = {annotating_value}
        for annotating_value_variant in annotating_value_variants:
            extended_annotations[annotating_value_variant] = annotated_resource
    extended_annotations = dict(sorted(extended_annotations.items(), reverse=True))
    
    document = fitz.open(document_path)
    for page in tqdm(document):
        # print('Page', page.number)
        annotated_rects_on_page = set()
        for annotating_value, annotating_resource in extended_annotations.items():
            __add_annotation_to_page(
                page=page,
                annotated_rects=annotated_rects_on_page,
                annotating_resource=annotating_resource,
                annotating_value=annotating_value)
                
    document.save(annotated_document_path)
            

annotate_pdf_document_with_ontology(
    document_path='/Users/pawel.garbacz/Library/CloudStorage/OneDrive-MakoLabS.A/idmp/ISO Standards/ISO_11616_2017(en).pdf',
    ontology_location='https://spec.pistoiaalliance.org/idmp/ontology/master/latest/QuickIDMPDev.ttl',
    annotated_document_path='ISO_11616_2017(en)_annotated.pdf',
    filter = 'spec.pistoiaalliance.org')
