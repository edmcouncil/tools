from rdflib import RDFS, SKOS

IS_A_COPULA = ' is a '
IS_COPULA = ' is '
MEANS_COPULA = ' means '

ONTOLOGY_PREFIX = 'ontology'
ONTOLOGY_IRI = 'https://spec.edmcouncil.org/ontology/'
PREFIX_DECLARATION = '@prefix ' + ONTOLOGY_PREFIX + '<' + ONTOLOGY_IRI + '>.'

COMMON_PREFIX_DECLARATIONS = \
    """@prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix xml: <http://www.w3.org/XML/1998/namespace> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
    @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    @prefix skos: <http://www.w3.org/2004/02/skos/core#> .
    @prefix dct: <http://purl.org/dc/terms/> .
    @prefix sm: <http://www.omg.org/techprocess/ab/SpecificationMetadata/> ."""

PROMPT_SEPARATOR = '\n###\n'
COMPLETION_SEPARATOR = '\n|||\n'

LABELS_PROPERTY = RDFS.label
DEFINITIONS_PROPERTY = SKOS.definition
