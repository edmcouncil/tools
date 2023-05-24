import json
import logging
import os
import re
import sys
import time

import wikibase_api.api
from rdflib import Graph, RDFS, URIRef, OWL, RDF, XSD
from rdflib.term import Identifier, Literal, BNode, Node
from tqdm import tqdm
from wikibase_api import Wikibase

wiki_label_property = RDFS.label
wiki_main_language = 'en'
wiki_description_property = URIRef('https://onto.kul.pl/ontohgis/isDefinedByLiteral')
ignored_namespace = 'http://purl.org/dc/terms/'
wiki_description_max_length = 250
wiki_description_truncate_sign = '...'
wiki_timeout = 1200


def process_triple(triple: tuple):
    subject = triple[0]
    predicate = triple[1]
    object = triple[2]
    
    if subject in ignored_resources:
        return
    
    if predicate in ignored_resources:
        return
    
    if object in ignored_resources:
        return
    
    if predicate == wiki_label_property:
        return
    
    if ignored_namespace in str(subject):
        logging.info(msg='I will ignore a triple because its subject is out-of-scope.')
        ignored_resources.add(subject)
        return
    if ignored_namespace in str(predicate):
        logging.info(msg='I will ignore a triple because its predicate is out-of-scope.')
        ignored_resources.add(predicate)
        return
    
    if ignored_namespace in str(object):
        logging.info(msg='I will ignore a triple because its object is out-of-scope.')
        ignored_resources.add(object)
        return
    
    if isinstance(subject, BNode):
        logging.info(msg='I will ignore a triple because its subject is a BNode.')
        ignored_resources.add(subject)
        return
    if isinstance(predicate, BNode):
        logging.info(msg='I will ignore a triple because its predicate is a BNode.')
        ignored_resources.add(predicate)
        return
    if isinstance(object, BNode):
        logging.info(msg='I will ignore a triple because its object is a BNode.')
        ignored_resources.add(object)
        return

    subject_wiki = get_or_create_wiki_from_resource(resource=subject)
    if subject_wiki is None:
        # logging.warning(msg='I will ignore a triple because its subject cannot be found in wiki: ' + str(subject))
        ignored_resources.add(subject)
        return
    if subject_wiki == subject:
        logging.warning(msg='I will ignore a triple because its subject looks like a literal: ' + str(subject))
        ignored_resources.add(subject)
        return

    predicate_wiki = get_or_create_wiki_from_resource(resource=predicate)
    if predicate_wiki is None:
        # logging.warning(msg='I will ignore a triple because its predicate cannot be found in wiki: ' + str(predicate))
        ignored_resources.add(predicate)
        return
    if predicate_wiki == predicate:
        logging.warning(msg='I will ignore a triple because its predicate looks like a literal: ' + str(predicate))
        ignored_resources.add(predicate)
        return
    
    if isinstance(object, Literal):
        is_object_literal = True
        wiki_value = str(object.value)
        wiki_value = wiki_value.replace('\n', '')
        wiki_value = wiki_value.replace('\r', '')
        wiki_value = wiki_value.replace('\t', ' ')
        wiki_value = wiki_value.strip()
        if len(wiki_value) == 0:
            logging.info(msg='I will ignore a triple because its object is a literal of 0 length.')
            ignored_resources.add(object)
            return
    else:
        is_object_literal = False
        object_wiki = get_or_create_wiki_from_resource(resource=object)
        if object_wiki is None:
            wiki_value = str(object)
        elif object_wiki == object:
            wiki_value = str(object)
            is_object_literal = True
        else:
            wiki_value = get_wiki_value(object_wiki=object_wiki)

    if not is_object_literal:
        if predicate not in item_wiki_properties:
            wiki_value = str(object)
    
    try:
        response = wikibase.claim.add(
            entity_id=subject_wiki,
            property_id=predicate_wiki,
            value=wiki_value)
        
    except Exception as exception:
        logging.warning(msg='ERR: process_triple:wikibase.claim.add(' + '|'.join(triple) + ')(' + str(subject_wiki) + '|' + str(predicate_wiki) + '|' + str(wiki_value) + '): ' + str(exception))
        return

    if not response['success']:
        logging.warning(msg='WARN: wikibase.claim.add(' + '|'.join(triple) + '): ' + str(response))
        return

    claim_id = response['claim']['id']
    
    if is_object_literal:
        if object.language:
            try:
                wikibase.qualifier.add(claim_id=claim_id,property_id=language_property_wiki,value=object.language)
            except Exception as exception:
                logging.warning(msg='ERR: wikibase.qualifier.add(' + str(exception))
                return
    
    if (subject, predicate, object) in annotation_map:
        annotating_property = annotation_map[(subject, predicate, object)][0]
        annotating_value = annotation_map[(subject, predicate, object)][1]
        
        annotating_property_wiki = get_or_create_wiki_from_resource(resource=annotating_property)
        if isinstance(annotating_value, Literal):
            annotating_value_wiki = annotating_value
        else:
            annotating_value_wiki = get_or_create_wiki_from_resource(resource=annotating_value)

        try:
            wikibase.qualifier.add(claim_id=claim_id, property_id=annotating_property_wiki, value=get_wiki_value(annotating_value_wiki))
        except Exception as exception:
            logging.warning(msg='ERR: wikibase.qualifier.add(' + str(exception))
            return
    

def get_wiki_value(object_wiki: str) -> str:
    is_object_wiki = re.search(pattern=re.compile(r'[A-Z]\d+'), string=object_wiki)
    if is_object_wiki is not None:
        if str(object_wiki).startswith('Q'):
            numeric_wiki_id_str = str(object_wiki).replace('Q', '')
            numeric_wiki_id = int(numeric_wiki_id_str)
            wiki_value = {"entity-type": "item", "numeric-id": numeric_wiki_id}
            return wiki_value
        
        if str(object_wiki).startswith('P'):
            numeric_wiki_id_str = str(object_wiki).replace('P', '')
            numeric_wiki_id = int(numeric_wiki_id_str)
            wiki_value = {"entity-type": "property", "numeric-id": numeric_wiki_id}
            return wiki_value
        
    return object_wiki

def create_wiki_for_resource(resource: Identifier) -> object:
    if isinstance(resource, URIRef):
        annotations = get_relevant_annotations(resource=resource)
        is_item_wiki_property = False
        if resource in rdf_resources_as_wiki_items:
            entity_type = 'item'
            try:
                response = wikibase.entity.add(entity_type=entity_type, content=annotations)
            except Exception as exception:
                logging.warning(msg='ERR: wikibase.entity.add(' + str(resource) + '): ' + str(exception))
                return None
        elif resource in rdf_resources_as_wiki_properties:
            entity_type = 'property'
            wiki_datatype = get_wiki_datatype(property=resource)
            if wiki_datatype != 'string':
                is_item_wiki_property = True
            annotations['datatype'] = wiki_datatype
            
            try:
                response = wikibase.entity.add(entity_type=entity_type, content=annotations)
            except Exception as exception:
                logging.warning(msg='ERR: wikibase.entity.add(' + str(resource) + '): ' + str(exception) + ' I will ignore it (and all triples where it occurs).')
                return None
        else:
            logging.info(msg='I was not able to classify: ' + str(resource) + '.')
            return None
        
        if not response['success']:
            logging.warning(msg='WARN: wikibase.entity.add(' + str(resource) + '): ' + str(response))
            return None
        
        wiki_id = response['entity']['id']
        rdf_to_wiki_map[resource] = wiki_id
        wiki_to_rdf_map[wiki_id] = resource
        if is_item_wiki_property:
            item_wiki_properties.add(resource)
        
        try:
            response = wikibase.claim.add(
                entity_id=wiki_id,
                property_id=external_origin_property_wiki,
                value=resource)
        except Exception as exception:
            logging.warning(
                msg='ERR: wikibase.claim.add(' + '|'.join(triple) + '), external source="' + str(external_origin_property_wiki) + '": ' + str(
                    exception))
            return
        
        return wiki_id
    else:
        return resource


def get_relevant_annotations(resource: URIRef) -> dict:
    annotations = dict()
    wiki_labels = \
        get_relevant_annotations_for_type(
            resource=resource,
            annotation_type=wiki_label_property,
            are_annotations_unique=True)
    annotations['labels'] = wiki_labels
    wiki_descriptions = \
        get_relevant_annotations_for_type(
            resource=resource,
            annotation_type=wiki_description_property,
            annotation_max_length=wiki_description_max_length)
    annotations['descriptions'] = wiki_descriptions
    
    return annotations


def get_relevant_annotations_for_type(
        resource: URIRef,
        annotation_type: URIRef,
        annotation_max_length=sys.maxsize,
        are_annotations_unique=False) -> dict:
    annotations = graph.objects(subject=resource, predicate=annotation_type)
    wiki_annotations = dict()
    for annotation in annotations:
        if isinstance(annotation, URIRef):
            continue
        else:
            annotation_language = annotation.language
            if annotation_language is None:
                annotation_language = wiki_main_language
            annotation_value = str(annotation.value).strip()
            if len(annotation_value) > annotation_max_length:
                truncate_treshold = annotation_max_length - 6
                annotation_value = annotation_value[0:truncate_treshold] + wiki_description_truncate_sign
        if are_annotations_unique:
            wiki_annotation = \
                get_wiki_annotation(
                    annotation_value=annotation_value,
                    annotation_language=annotation_language,
                    annotation_type=annotation_type)
        else:
            wiki_annotation = annotation_value
        wiki_annotations[annotation_language] = dict()
        wiki_annotations[annotation_language]['language'] = annotation_language
        wiki_annotations[annotation_language]['value'] = wiki_annotation
    
    return wiki_annotations


def get_wiki_annotation(
        annotation_value: str,
        annotation_language: str,
        annotation_type: URIRef) -> str:
    if annotation_type in rdf_annotation_map:
        annotation_type_map = rdf_annotation_map[annotation_type]
    else:
        annotation_type_map = dict()
        rdf_annotation_map[annotation_type] = annotation_type_map
    if annotation_language in annotation_type_map:
        annotations_for_language = annotation_type_map[annotation_language]
    else:
        annotations_for_language = dict()
        annotation_type_map[annotation_language] = annotations_for_language
    if annotation_value in annotations_for_language:
        annotations_for_language[annotation_value] = \
            annotations_for_language[annotation_value] + 1
        unique_label_value = annotation_value + ' ' + '(' + str(annotations_for_language[annotation_value]) + ')'
    else:
        rdf_annotation_map[annotation_type][annotation_language][annotation_value] = 1
        unique_label_value = annotation_value
    
    return unique_label_value


def get_or_create_wiki_from_resource(resource: Identifier) -> object:
    if resource in rdf_to_wiki_map:
        wiki_entity = rdf_to_wiki_map[resource]
    else:
        wiki_entity = create_wiki_for_resource(resource=resource)
    return wiki_entity


def get_wiki_datatype(property: URIRef) -> str:
    property_ranges = set(graph.objects(subject=property, predicate=RDFS.range))
    if len(property_ranges) == 0:
        super_properties = graph.transitive_objects(subject=property, predicate=RDFS.subPropertyOf)
        for super_property in super_properties:
            property_ranges = property_ranges.union(set(graph.objects(subject=super_property, predicate=RDFS.range)))
    if OWL.Class in property_ranges:
        return 'wikibase-item'
    if OWL.ObjectProperty in property_ranges:
        return 'wikibase-property'
    if OWL.DatatypeProperty in property_ranges:
        return 'wikibase-property'
    if OWL.AnnotationProperty in property_ranges:
        return 'wikibase-property'
    if RDFS.Literal in property_ranges:
        return 'string'
    if RDFS.Class in property_ranges:
        return 'wikibase-item'
    if RDFS.Resource in property_ranges:
        return 'string'
    if RDF.Property in property_ranges:
        return 'wikibase-property'
    if RDF.List in property_ranges:
        return 'wikibase-property'
    if XSD.anyURI in property_ranges:
        return 'wikibase-item'
    
    for property_range in property_ranges:
        property_range_types = set(graph.objects(subject=property_range, predicate=RDF.type))
        if OWL.Class in property_range_types or RDFS.Class in property_range_types:
            return 'wikibase-item'
            
    if property in annotation_properties:
        return 'string'
    if property in data_properties:
        return 'string'
    if property in object_properties:
        return 'wikibase-item'
    
    return 'string'


def process_owl_restriction(owl_restriction: Node):
    restricting_properties = list(graph.objects(subject=owl_restriction, predicate=OWL.onProperty))
    if len(list(restricting_properties)) > 1:
        logging.exception(msg='Something is very wrong - I got an OWL restriction with multiple restricting properties.')
        return
    restricting_property = restricting_properties[0]
    if restricting_property not in rdf_to_wiki_map:
        logging.warning(msg='I could not process an OWL restriction because is restricting property is not found in wiki.')
        return
    restricting_property_wiki = rdf_to_wiki_map[restricting_property]
    
    onClass_classes = list(graph.objects(subject=owl_restriction, predicate=OWL.onClass))
    if len(list(onClass_classes)) > 1:
        logging.exception(msg='Something is very wrong - I got an OWL restriction with multiple restricting classes.')
        return
    someValuesFrom_classes = list(graph.objects(subject=owl_restriction, predicate=OWL.someValuesFrom))
    if len(list(someValuesFrom_classes)) > 1:
        logging.exception(msg='Something is very wrong - I got an OWL restriction with multiple restricting classes.')
        return
    hasValue_classes = list(graph.objects(subject=owl_restriction, predicate=OWL.hasValue))
    if len(list(hasValue_classes)) > 1:
        logging.exception(msg='Something is very wrong - I got an OWL restriction with multiple restricting classes.')
        return

    restricting_resource = None
    if len(onClass_classes) == 1:
        restricting_resource = onClass_classes[0]
    if len(someValuesFrom_classes) == 1:
        restricting_resource = someValuesFrom_classes[0]
    if len(hasValue_classes) == 1:
        restricting_resource = hasValue_classes[0]

    if not isinstance(restricting_resource, URIRef):
        logging.info(msg='Ignoring an OWL restriction because its restricting class is not an IRI.')
        return
    if restricting_resource not in rdf_to_wiki_map:
        logging.warning(msg='I could not process an OWL restriction because is restricting class is not found in wiki.')
        return
    restricting_class_wiki = rdf_to_wiki_map[restricting_resource]
    
    restricted_classes = list(graph.subjects(object=owl_restriction, predicate=RDFS.subClassOf))
    for restricted_class in restricted_classes:
        if restricted_class in rdf_to_wiki_map:
            restricted_class_wiki = rdf_to_wiki_map[restricted_class]
            try:
                wiki_value = \
                    get_wiki_value(object_wiki=restricting_class_wiki)
                
                response = wikibase.claim.add(
                    entity_id=restricted_class_wiki,
                    property_id=restricting_property_wiki,
                    value=wiki_value,
                    snak_type='value')
            except Exception as exception:
                logging.warning(msg='ERR: process_owl_restriction:wikibase.claim.add(' + str(wiki_value) + '): ' + str(exception))
                continue
            else:
                logging.info(msg='OWL restriction was successfully transferred to wiki.')
        else:
            logging.warning(msg='I could not process a an OWL restriction because the the resticted class is not an IRI.')
            return
    else:
        logging.info(msg='I ignore an OWL restriction because its type is out-of scope.')
        return


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.WARN,datefmt='%Y%m%d_%H:%M:%S')

    logging.info(msg='Authenticating access to wikidata')
    logging.info(msg='DBG: auth')
    login_credentials = {'bot_username': os.environ.get('WIKI_LOGIN'), 'bot_password': os.environ.get('WIKI_PASSWORD')}
    wikibase = Wikibase(api_url='https://cidoc.wiki.kul.pl/w/api.php', login_credentials=login_credentials)

    
    external_origin_property_content = \
        {
            "labels":
                {"en": {"language": "en", "value": "has external origin"}},
            "descriptions":
                {
                "en": {"language": "en", "value": "indicates the external source of a wikibase entity (if any)"}},
            "datatype": "url"
        }
    response = wikibase.entity.add(entity_type='property', content=external_origin_property_content)
    external_origin_property_wiki = response['entity']['id']

    language_property_content = \
        {
            "labels":
                {"en": {"language": "en", "value": "language"}},
            "datatype": "string"
        }
    response = wikibase.entity.add(entity_type='property', content=language_property_content)
    language_property_wiki = response['entity']['id']
    
    logging.info(msg='Uploading ontology')
    graph = Graph()
    graph.parse('ontohgis.ttl')
    rdf = Graph()
    rdf.parse('http://www.w3.org/1999/02/22-rdf-syntax-ns')
    rdfs = Graph()
    rdfs.parse('http://www.w3.org/2000/01/rdf-schema')
    owl = Graph()
    owl.parse('http://www.w3.org/2002/07/owl')
    skos = Graph()
    skos.parse('http://www.w3.org/2004/02/skos/core')
    dct = Graph()
    dct.parse('https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_terms.rdf')
    dce = Graph()
    dce.parse('https://www.dublincore.org/specifications/dublin-core/dcmi-terms/dublin_core_elements.rdf')
    
    graph = graph + rdf + rdfs + owl + skos + dct + dce
    
    rdf_to_wiki_map = dict()
    wiki_to_rdf_map = dict()
    item_wiki_properties = set()
    rdf_annotation_map = dict()
    all_nodes = graph.all_nodes()
    ontologies = set(graph.subjects(predicate=RDF.type, object=OWL.Ontology))
    owl_classes = set(graph.subjects(predicate=RDF.type, object=OWL.Class))
    rdfs_classes = set(graph.subjects(predicate=RDF.type, object=RDFS.Class))
    classes = owl_classes.union(rdfs_classes)
    individuals = set(graph.subjects(predicate=RDF.type, object=OWL.NamedIndividual))
    rdfs_datatypes = set(graph.subjects(predicate=RDF.type, object=RDFS.Datatype))
    xml_datatypes = set([xsd for xsd in dir(XSD)])
    datatypes = rdfs_datatypes.union(xml_datatypes)
    object_properties = set(graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty))
    data_properties = set(graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty))
    annotation_properties = set(graph.subjects(predicate=RDF.type, object=OWL.AnnotationProperty))
    ontology_properties = set(graph.subjects(predicate=RDF.type, object=OWL.OntologyProperty))
    rdf_properties = set(graph.subjects(predicate=RDF.type, object=RDF.Property))
    owl_axioms = set(graph.subjects(predicate=RDF.type, object=OWL.Axiom))
    annotation_map = dict()
    for owl_axiom in owl_axioms:
        source = list(graph.objects(subject=owl_axiom, predicate=OWL.annotatedSource))[0]
        axiom_property = list(graph.objects(subject=owl_axiom, predicate=OWL.annotatedProperty))[0]
        target = list(graph.objects(subject=owl_axiom, predicate=OWL.annotatedTarget))[0]
        properties = list(graph.predicate_objects(subject=owl_axiom))
        annotated_property = None
        for property in properties:
            if property[0] == OWL.annotatedSource:
                continue
            if property[0] == OWL.annotatedProperty:
                continue
            if property[0] == OWL.annotatedTarget:
                continue
            if property[0] == RDF.type:
                continue
            annotated_property = property[0]
            annotated_value = property[1]
            break
        annotation_map[(source, axiom_property, target)] = (annotated_property, annotated_value)

    rdf_resources_as_wiki_properties = rdf_properties.union(object_properties).union(data_properties).union(annotation_properties).union(ontology_properties)
    # all_nodes_except_for_rdf_resources_as_wiki_properties = all_nodes.difference(rdf_resources_as_wiki_properties)
    rdf_resources_as_wiki_items = ontologies.union(classes).union(individuals).union(datatypes)
    
    if len(ontologies.intersection(rdf_resources_as_wiki_properties)) > 0:
        logging.warning(msg='Punning detected - some ontologies are properties. The former classifications will be ignored.')
        ontologies.difference_update(rdf_resources_as_wiki_properties)
    
    if len(classes.intersection(rdf_resources_as_wiki_properties)) > 0:
        logging.warning(msg='Punning detected - some classes are properties. The former classifications will be ignored.')
        classes.difference_update(rdf_resources_as_wiki_properties)
        
    if len(individuals.intersection(rdf_resources_as_wiki_properties)) > 0:
        logging.warning(msg='Punning detected - some individuals are properties. The former classifications will be ignored.')
        individuals.difference_update(rdf_resources_as_wiki_properties)
    
    ignored_resources = set()
    
    logging.info(msg="Converting ontology's triples to wikidata")
    start = time.time()
    for triple in tqdm(graph):
        end = time.time()
        if end - start > wiki_timeout:
            wikibase.api.session.close()
            del wikibase
            logging.info(msg='DBG: auth')
            wikibase = Wikibase(api_url='https://cidoc.wiki.kul.pl/w/api.php', login_credentials=login_credentials)
            start = time.time()
        process_triple(triple)

    logging.info(msg="Converting ontology's OWL restrictions to wikidata")
    start = time.time()
    owl_restrictions = set(graph.subjects(predicate=RDF.type, object=OWL.Restriction))
    for owl_restriction in tqdm(owl_restrictions):
        end = time.time()
        if end-start > wiki_timeout:
            wikibase.api.session.close()
            del wikibase
            logging.info(msg='DBG: auth')
            wikibase = Wikibase(api_url='https://cidoc.wiki.kul.pl/w/api.php', login_credentials=login_credentials)
            start = time.time()
        process_owl_restriction(owl_restriction=owl_restriction)
