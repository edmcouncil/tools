import logging
import os
import re
import sys
import time
import uuid

from rdflib import RDFS, URIRef, Graph, RDF, XSD, OWL, BNode, Literal
from rdflib.term import Identifier, Node
from tqdm import tqdm
from wikibase_api import Wikibase

WIKIBASE_ITEM_TYPE = 'wikibase-item'
WIKIBASE_PROPERTY_TYPE = 'wikibase-property'
WIKIBASE_URL_TYPE = 'url'
WIKIBASE_STRING_TYPE = 'string'


class TransformationConfiguration:
    def __init__(self):
        self.wiki_label_property = RDFS.label
        self.wiki_main_language = 'en'
        self.wiki_description_property = URIRef('https://onto.kul.pl/ontohgis/isDefinedByLiteral')
        self.ignored_namespace = 'http://purl.org/dc/terms/'
        self.wiki_description_max_length = 250
        self.wiki_description_truncate_sign = '...'
        self.wiki_timeout = 1200
        self.dry_run = False
        
        self.login_credentials = None
        self.external_origin_property_wiki = None
        self.language_property_wiki = None
        self.wikibase = None
        self.optionality_property = None
        
        self.rdf_types_to_wiki_datatypes_map = \
            {
                XSD.anyURI: WIKIBASE_URL_TYPE,
                # RDF.List: WIKIBASE_PROPERTY_TYPE,
                # RDF.Bag: WIKIBASE_PROPERTY_TYPE,
                # RDF.Alt: WIKIBASE_PROPERTY_TYPE,
                RDF.Property: WIKIBASE_PROPERTY_TYPE,
                RDFS.Class: WIKIBASE_ITEM_TYPE,
                RDFS.Literal: WIKIBASE_STRING_TYPE,
                # RDFS.Container: WIKIBASE_PROPERTY_TYPE,
                RDFS.Resource: WIKIBASE_STRING_TYPE,
                RDFS.Datatype: WIKIBASE_STRING_TYPE,
                OWL.Ontology: WIKIBASE_ITEM_TYPE,
                OWL.Class: WIKIBASE_ITEM_TYPE,
                OWL.ObjectProperty: WIKIBASE_PROPERTY_TYPE,
                OWL.DatatypeProperty: WIKIBASE_PROPERTY_TYPE,
                OWL.AnnotationProperty: WIKIBASE_PROPERTY_TYPE,
                OWL.Thing: WIKIBASE_ITEM_TYPE
            }
        
        
class TransformationScope:
    def __init__(self, graph: Graph, config: TransformationConfiguration):
        self.graph = graph
        self.config = config
        
        self.ontologies = set()
        self.classes = set()
        self.individuals = set()
        self.datatypes = set()
        self.properties = set()
        self.object_properties = set()
        self.axioms = set()
        self.annotations = dict()
        self.all_nodes = set()
        self.ignored_resources = set()
        
        self.rdf_to_wiki_map = dict()
        self.wiki_to_rdf_map = dict()
        self.item_wiki_properties = set()
        self.rdf_annotation_map = dict()
    
        
    def getwikiable_items(self):
        return self.ontologies.union(self.individuals).union(self.classes).union(self.datatypes)
    
    def getwikiable_properties(self):
        return self.properties


def process_triple(triple: tuple, scope: TransformationScope):
    subject = triple[0]
    predicate = triple[1]
    object = triple[2]

    if subject in scope.ignored_resources:
        return
    if predicate in scope.ignored_resources:
        return
    if object in scope.ignored_resources:
        return
    if predicate == scope.config.wiki_label_property:
        return

    if scope.config.ignored_namespace in str(subject):
        logging.info(msg='I will ignore a triple because its subject is out-of-scope.')
        scope.ignored_resources.add(subject)
        return
    if scope.config.ignored_namespace in str(predicate):
        logging.info(msg='I will ignore a triple because its predicate is out-of-scope.')
        scope.ignored_resources.add(predicate)
        return

    if scope.config.ignored_namespace in str(object):
        logging.info(msg='I will ignore a triple because its object is out-of-scope.')
        scope.ignored_resources.add(object)
        return

    if isinstance(subject, BNode):
        logging.info(msg='I will ignore a triple because its subject is a BNode.')
        scope.ignored_resources.add(subject)
        return
    if isinstance(predicate, BNode):
        logging.info(msg='I will ignore a triple because its predicate is a BNode.')
        scope.ignored_resources.add(predicate)
        return
    if isinstance(object, BNode):
        logging.info(msg='I will ignore a triple because its object is a BNode.')
        scope.ignored_resources.add(object)
        return

    subject_wiki = get_or_create_wiki_from_resource(resource=subject, scope=scope)
    if subject_wiki is None:
        # logging.warning(msg='I will ignore a triple because its subject cannot be found in wiki: ' + str(subject))
        scope.ignored_resources.add(subject)
        return
    if subject_wiki == subject:
        logging.warning(msg='I will ignore a triple because its subject looks like a literal: ' + str(subject))
        scope.ignored_resources.add(subject)
        return

    predicate_wiki = get_or_create_wiki_from_resource(resource=predicate, scope=scope)
    if predicate_wiki is None:
        scope.ignored_resources.add(predicate)
        return
    if predicate_wiki == predicate:
        logging.warning(msg='I will ignore a triple because its predicate looks like a literal: ' + str(predicate))
        scope.ignored_resources.add(predicate)
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
            scope.ignored_resources.add(object)
            return
    else:
        is_object_literal = False
        object_wiki = get_or_create_wiki_from_resource(resource=object, scope=scope)
        if object_wiki is None:
            wiki_value = str(object)
        elif object_wiki == object:
            wiki_value = str(object)
            is_object_literal = True
        else:
            wiki_value = get_wiki_value(object_wiki=object_wiki)

    if not is_object_literal:
        if predicate not in scope.properties:
            wiki_value = str(object)

    if scope.config.dry_run:
        return

    try:
        response = scope.config.wikibase.claim.add(
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
                scope.config.wikibase.qualifier.add(claim_id=claim_id,property_id=scope.config.language_property_wiki,value=object.language)
            except Exception as exception:
                logging.warning(msg='ERR: wikibase.qualifier.add(' + str(exception))
                return

    if (subject, predicate, object) in scope.annotations:
        annotating_property = scope.annotations[(subject, predicate, object)][0]
        annotating_value = scope.annotations[(subject, predicate, object)][1]

        annotating_property_wiki = get_or_create_wiki_from_resource(resource=annotating_property, scope=scope)
        if isinstance(annotating_value, Literal):
            annotating_value_wiki = annotating_value
        else:
            annotating_value_wiki = get_or_create_wiki_from_resource(resource=annotating_value, scope=scope)

        try:
            scope.config.wikibase.qualifier.add(claim_id=claim_id, property_id=annotating_property_wiki, value=get_wiki_value(annotating_value_wiki))
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


def create_wiki_for_resource(resource: Identifier, scope: TransformationScope) -> object:
    if isinstance(resource, URIRef):
        annotations = get_relevant_annotations(resource=resource, scope=scope)
        if resource in scope.getwikiable_items():
            entity_type = 'item'
        elif resource in scope.getwikiable_properties():
            entity_type = 'property'
            wiki_datatype = get_wiki_datatype_for_property(property=resource, scope=scope)
            annotations['datatype'] = wiki_datatype
        else:
            logging.info(msg='I was not able to classify: ' + str(resource) + '.')
            return None
        if scope.config.dry_run:
            wiki_id = str(uuid.uuid4())
        else:
            try:
                response = scope.config.wikibase.entity.add(entity_type=entity_type, content=annotations)
            except Exception as exception:
                logging.warning(msg='ERR: wikibase.entity.add(' + str(resource) + '): ' + str(exception))
                return None
            if not response['success']:
                logging.warning(msg='WARN: wikibase.entity.add(' + str(resource) + '): ' + str(response))
                return None
            
            wiki_id = response['entity']['id']
            
            try:
                scope.config.wikibase.claim.add(
                    entity_id=wiki_id,
                    property_id=scope.config.external_origin_property_wiki,
                    value=resource)
            except Exception as exception:
                logging.warning(
                    msg='ERR: wikibase.claim.add(' + '|'.join(wiki_id) + '), external source="' + str(scope.config.external_origin_property_wiki) + '": ' + str(
                        exception))
                return None
        
        scope.rdf_to_wiki_map[resource] = wiki_id
        scope.wiki_to_rdf_map[wiki_id] = resource
        
        return wiki_id
    else:
        return resource


def get_relevant_annotations(resource: URIRef, scope: TransformationScope) -> dict:
    annotations = dict()
    wiki_labels = \
        get_relevant_annotations_for_type(
            resource=resource,
            annotation_type=scope.config.wiki_label_property,
            are_annotations_unique=True, scope=scope)
    if len(wiki_labels) == 0:
        iri_fragment = resource.fragment
        wiki_labels['en'] = dict()
        wiki_labels['en']['language'] = 'en'
        wiki_labels['en']['value'] = iri_fragment
    annotations['labels'] = wiki_labels
    wiki_descriptions = \
        get_relevant_annotations_for_type(
            resource=resource,
            annotation_type=scope.config.wiki_description_property,
            annotation_max_length=scope.config.wiki_description_max_length,
            scope=scope)
    annotations['descriptions'] = wiki_descriptions

    return annotations


def get_relevant_annotations_for_type(
        resource: URIRef,
        annotation_type: URIRef,
        scope: TransformationScope,
        annotation_max_length=sys.maxsize,
        are_annotations_unique=False) -> dict:
    annotations = scope.graph.objects(subject=resource, predicate=annotation_type)
    wiki_annotations = dict()
    for annotation in annotations:
        if isinstance(annotation, URIRef):
            continue
        else:
            annotation_language = annotation.language
            if annotation_language is None:
                annotation_language = scope.config.wiki_main_language
            annotation_value = str(annotation.value).strip()
            if len(annotation_value) > annotation_max_length:
                truncate_treshold = annotation_max_length - 6
                annotation_value = annotation_value[0:truncate_treshold] + scope.config.wiki_description_truncate_sign
        if are_annotations_unique:
            wiki_annotation = \
                get_wiki_annotation(
                    annotation_value=annotation_value,
                    annotation_language=annotation_language,
                    annotation_type=annotation_type,
                    scope=scope)
        else:
            wiki_annotation = annotation_value
        wiki_annotations[annotation_language] = dict()
        wiki_annotations[annotation_language]['language'] = annotation_language
        wiki_annotations[annotation_language]['value'] = wiki_annotation

    return wiki_annotations


def get_wiki_annotation(
        annotation_value: str,
        annotation_language: str,
        annotation_type: URIRef,
        scope: TransformationScope) -> str:
    if annotation_type in scope.rdf_annotation_map:
        annotation_type_map =scope.rdf_annotation_map[annotation_type]
    else:
        annotation_type_map = dict()
        scope.rdf_annotation_map[annotation_type] = annotation_type_map
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
        scope.rdf_annotation_map[annotation_type][annotation_language][annotation_value] = 1
        unique_label_value = annotation_value

    return unique_label_value


def get_or_create_wiki_from_resource(resource: Identifier, scope: TransformationScope) -> object:
    if resource in scope.rdf_to_wiki_map:
        wiki_entity = scope.rdf_to_wiki_map[resource]
    else:
        wiki_entity = create_wiki_for_resource(resource=resource, scope=scope)
    return wiki_entity


def get_wiki_datatype_for_property(property: URIRef, scope: TransformationScope) -> str:
    property_ranges = set(scope.graph.objects(subject=property, predicate=RDFS.range))
    if len(property_ranges) == 0:
        super_properties = scope.graph.transitive_objects(subject=property, predicate=RDFS.subPropertyOf)
        for super_property in super_properties:
            property_ranges = property_ranges.union(set(scope.graph.objects(subject=super_property, predicate=RDFS.range)))
            
    wiki_datatype = try_to_get_wiki_datatype_from_rdf_types(rdf_types=property_ranges)
    if len(wiki_datatype) > 0:
        return wiki_datatype
    
    property_range_types = set()
    for property_range in property_ranges:
        property_range_types = property_range_types.union(set(scope.graph.objects(subject=property_range, predicate=RDF.type)))
    
    wiki_datatype = try_to_get_wiki_datatype_from_rdf_types(rdf_types=property_range_types)
    if len(wiki_datatype) > 0:
        return wiki_datatype
    
    if property in scope.object_properties:
        return WIKIBASE_ITEM_TYPE

    return WIKIBASE_STRING_TYPE


def try_to_get_wiki_datatype_from_rdf_types(rdf_types: set) -> str:
    wiki_datatype_candidates = set()
    for property_range in rdf_types:
        if property_range in scope.config.rdf_types_to_wiki_datatypes_map:
            wiki_datatype_candidates.add(scope.config.rdf_types_to_wiki_datatypes_map[property_range])
    
    if len(wiki_datatype_candidates) > 1:
        logging.error(msg='Property' + str(property) + ' has mixed ranges.')
        return str()
    
    if len(wiki_datatype_candidates) == 1:
        return list(wiki_datatype_candidates)[0]
    
    return str()


def process_owl_restriction(owl_restriction: Node, scope: TransformationScope):
    restricting_properties = list(scope.graph.objects(subject=owl_restriction, predicate=OWL.onProperty))
    restricting_property = restricting_properties[0]
    if restricting_property not in scope.rdf_to_wiki_map:
        logging.warning(msg='I could not process an OWL restriction because is restricting property is not found in wiki.')
        return
    restricting_property_wiki = scope.rdf_to_wiki_map[restricting_property]

    onClass_classes = list(scope.graph.objects(subject=owl_restriction, predicate=OWL.onClass))
    someValuesFrom_classes = list(scope.graph.objects(subject=owl_restriction, predicate=OWL.someValuesFrom))
    hasValue_classes = list(scope.graph.objects(subject=owl_restriction, predicate=OWL.hasValue))
    minCardinality = list(scope.graph.objects(subject=owl_restriction, predicate=OWL.minCardinality))
    minQCardinality = list(scope.graph.objects(subject=owl_restriction, predicate=OWL.minQualifiedCardinality))
    cardinality = list(scope.graph.objects(subject=owl_restriction, predicate=OWL.cardinality))
    qCardinality = list(scope.graph.objects(subject=owl_restriction, predicate=OWL.qualifiedCardinality))
    
    restricting_cardinality = None
    if len(minCardinality) == 1:
        restricting_cardinality = minCardinality[0]
    if len(minQCardinality) == 1:
        restricting_cardinality = minQCardinality[0]
    if len(cardinality) == 1:
        restricting_cardinality = cardinality[0]
    if len(qCardinality) == 1:
        restricting_cardinality = qCardinality[0]

    restricting_resource = None
    is_optional_restriction = False
    if len(onClass_classes) == 1:
        if restricting_cardinality:
            if restricting_cardinality == 0:
                is_optional_restriction = True
            restricting_resource = onClass_classes[0]
    if len(someValuesFrom_classes) == 1:
        restricting_resource = someValuesFrom_classes[0]
    if len(hasValue_classes) == 1:
        restricting_resource = hasValue_classes[0]

    if not isinstance(restricting_resource, URIRef):
        logging.info(msg='Ignoring an OWL restriction because its restricting class is not an IRI.')
        return
    if restricting_resource not in scope.rdf_to_wiki_map:
        logging.warning(msg='I could not process an OWL restriction because is restricting class is not found in wiki.')
        return
    restricting_class_wiki = scope.rdf_to_wiki_map[restricting_resource]

    restricted_classes = list(scope.graph.subjects(object=owl_restriction, predicate=RDFS.subClassOf))
    for restricted_class in restricted_classes:
        if restricted_class in scope.rdf_to_wiki_map:
            restricted_class_wiki = scope.rdf_to_wiki_map[restricted_class]
            
            if scope.config.dry_run:
                continue
            
            try:
                wiki_value = get_wiki_value(object_wiki=restricting_class_wiki)

                response = \
                    scope.config.wikibase.claim.add(
                        entity_id=restricted_class_wiki,
                        property_id=restricting_property_wiki,
                        value=wiki_value,
                        snak_type='value')
                
                if is_optional_restriction:
                    claim_id = response['claim']['id']
                    try:
                        scope.config.wikibase.qualifier.add(
                            claim_id=claim_id,
                            property_id=scope.config.optionality_property,
                            value='True')
                    except Exception as exception:
                        logging.warning(msg='ERR: wikibase.qualifier.add(' + str(exception))
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


def establish_wiki_connection(config: TransformationConfiguration):
    logging.info(msg='Authenticating access to wikidata')
    logging.info(msg='DBG: auth')
    login_credentials = {'bot_username': os.environ.get('WIKI_LOGIN'), 'bot_password': os.environ.get('WIKI_PASSWORD')}
    config.wikibase = Wikibase(api_url='https://cidoc.wiki.kul.pl/w/api.php', login_credentials=login_credentials)
    config.login_credentials = login_credentials


def add_wiki_infrastructure_properties(config: TransformationConfiguration):
    if config.dry_run:
        return
    external_origin_property_content = \
        {
            "labels":
                {"en": {"language": "en", "value": "has external origin"}},
            "descriptions":
                {
                "en": {"language": "en", "value": "indicates the external source of a wikibase entity (if any)"}},
            "datatype": "url"
        }
    response = config.wikibase.entity.add(entity_type='property', content=external_origin_property_content)
    config.external_origin_property_wiki = response['entity']['id']

    language_property_content = \
        {
            "labels":
                {"en": {"language": "en", "value": "language"}},
            "datatype": "string"
        }
    response = config.wikibase.entity.add(entity_type='property', content=language_property_content)
    config.language_property_wiki = response['entity']['id']
    
    optionality_property = \
        {
            "labels":
                {"en": {"language": "en", "value": "is optional"}},
            "datatype": "string"
        }
    response = config.wikibase.entity.add(entity_type='property', content=optionality_property)
    config.optionality_property = response['entity']['id']


def collect_all_rdf_resources(config: TransformationConfiguration, graph_iri: str) -> TransformationScope:
    logging.info(msg='Uploading ontology')
    
    graph = Graph()
    graph.parse(graph_iri)
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
    
    scope = TransformationScope(graph=graph, config=config)

    scope.all_nodes = graph.all_nodes()
    
    scope.ontologies = set(graph.subjects(predicate=RDF.type, object=OWL.Ontology))
    
    owl_classes = set(graph.subjects(predicate=RDF.type, object=OWL.Class))
    rdfs_classes = set(graph.subjects(predicate=RDF.type, object=RDFS.Class))
    scope.classes = owl_classes.union(rdfs_classes)
    
    scope.individuals = set(graph.subjects(predicate=RDF.type, object=OWL.NamedIndividual))
    
    rdfs_datatypes = set(graph.subjects(predicate=RDF.type, object=RDFS.Datatype))
    xml_datatypes = set([xsd for xsd in dir(XSD)])
    scope.datatypes = rdfs_datatypes.union(xml_datatypes)
    
    object_properties = set(graph.subjects(predicate=RDF.type, object=OWL.ObjectProperty))
    data_properties = set(graph.subjects(predicate=RDF.type, object=OWL.DatatypeProperty))
    annotation_properties = set(graph.subjects(predicate=RDF.type, object=OWL.AnnotationProperty))
    ontology_properties = set(graph.subjects(predicate=RDF.type, object=OWL.OntologyProperty))
    rdf_properties = set(graph.subjects(predicate=RDF.type, object=RDF.Property))
    scope.properties = ontology_properties.union(data_properties).union(annotation_properties).union(object_properties).union(rdf_properties)
    scope.object_properties = object_properties
    
    scope.axioms = set(graph.subjects(predicate=RDF.type, object=OWL.Axiom))
    annotation_map = dict()
    for axiom in scope.axioms:
        source = list(graph.objects(subject=axiom, predicate=OWL.annotatedSource))[0]
        axiom_property = list(graph.objects(subject=axiom, predicate=OWL.annotatedProperty))[0]
        target = list(graph.objects(subject=axiom, predicate=OWL.annotatedTarget))[0]
        properties = list(graph.predicate_objects(subject=axiom))
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
    scope.annotations = annotation_map

    if len(scope.ontologies.intersection(scope.properties)) > 0:
        logging.warning(msg='Punning detected - some ontologies are properties. The former classifications will be ignored.')
        scope.ontologies.difference_update(scope.properties)

    if len(scope.classes.intersection(scope.properties)) > 0:
        logging.warning(msg='Punning detected - some classes are properties. The former classifications will be ignored.')
        scope.classes.difference_update(scope.properties)

    if len(scope.individuals.intersection(scope.properties)) > 0:
        logging.warning(msg='Punning detected - some individuals are properties. The former classifications will be ignored.')
        scope.individuals.difference_update(scope.properties)
        
    return scope


def process_all_rdf_triples(scope: TransformationScope):
    logging.info(msg="Converting ontology's triples to wikidata")
    start = time.time()
    for triple in tqdm(scope.graph):
        if not scope.config.dry_run:
            end = time.time()
            if end - start > config.wiki_timeout:
                scope.config.wikibase.api.session.close()
                del scope.config.wikibase
                logging.info(msg='DBG: auth')
                scope.config.wikibase = Wikibase(api_url='https://cidoc.wiki.kul.pl/w/api.php', login_credentials=scope.config.login_credentials)
                start = time.time()
        process_triple(triple, scope)


def process_all_owl_restrictions(scope: TransformationScope):
    logging.info(msg="Converting ontology's OWL restrictions to wikidata")
    start = time.time()
    owl_restrictions = set(scope.graph.subjects(predicate=RDF.type, object=OWL.Restriction))
    for owl_restriction in tqdm(owl_restrictions):
        if not scope.config.dry_run:
            end = time.time()
            if end-start > scope.config.wiki_timeout:
                scope.config.wikibase.api.session.close()
                del scope.config.wikibase
                logging.info(msg='DBG: auth')
                scope.config.wikibase = Wikibase(api_url='https://cidoc.wiki.kul.pl/w/api.php', login_credentials=scope.config.login_credentials)
                start = time.time()
        process_owl_restriction(owl_restriction=owl_restriction, scope=scope)


if __name__ == "__main__":
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.WARN,datefmt='%Y%m%d_%H:%M:%S')
    
    config = TransformationConfiguration()
    # config.dry_run = True
    
    if not config.dry_run:
        establish_wiki_connection(config)
        add_wiki_infrastructure_properties(config=config)
    scope = collect_all_rdf_resources(config=config, graph_iri='ontohgis.ttl')
    process_all_rdf_triples(scope=scope)
    process_all_owl_restrictions(scope=scope)
    