import logging
import os.path
import xml.etree.ElementTree as ET
from rdflib import Graph, OWL, RDF


def __close_imports(ontology: Graph, imported_ontologies: set, stored_ontologies: dict):
    importing_imported_ontologies = ontology.subject_objects(predicate=OWL.imports)
    for importing_imported_ontology in importing_imported_ontologies:
        imported_ontology_iri = importing_imported_ontology[1]
        if imported_ontology_iri not in imported_ontologies:
            try:
                imported_ontologies.add(imported_ontology_iri)
                logging.info(msg='Importing ' + str(imported_ontology_iri))
                imported_ontology = Graph()
                imported_ontology.parse(imported_ontology_iri)
            except Exception as import_error:
                if str(imported_ontology_iri) in stored_ontologies:
                    imported_ontology.parse(stored_ontologies[str(imported_ontology_iri)])
                else:
                    logging.error(msg=import_error)
            imported_ontology_without_ontology_triples = __drop_ontology_triples(ontology=imported_ontology)
            ontology += imported_ontology_without_ontology_triples
            for prefix, namespace in imported_ontology.namespaces():
                if (prefix, namespace) not in ontology.namespaces():
                    ontology.bind(prefix=prefix, namespace=namespace)
            __close_imports(ontology=ontology, imported_ontologies=imported_ontologies, stored_ontologies=stored_ontologies)


def __drop_ontology_triples(ontology: Graph) -> Graph:
    ontology_without_ontology_triples = Graph()
    ontology_iris = set(ontology.subjects(predicate=RDF.type, object=OWL.Ontology))
    for (subject, predicate, object) in ontology:
        if not subject in ontology_iris:
            ontology_without_ontology_triples.add((subject, predicate, object))
    return ontology_without_ontology_triples


def __get_stored_ontologies(ontology_folder: str, catalog_file_path: str) -> dict:
    stored_ontologies = dict()
    catalog = ET.parse(source=catalog_file_path)
    for ontology_ref in catalog.getroot():
        stored_ontologies[ontology_ref.attrib['name']] = os.path.join(ontology_folder, ontology_ref.attrib['uri']).replace('/./', '/')
    return stored_ontologies


def merge(ontology_folder: str, ontology_file_path: str, catalog_file_path: str, merged_ontology_file_path: str):
    ontology = Graph()
    ontology.parse(source=ontology_file_path)
    merged_ontology = Graph() + ontology
    ontology.close()
    stored_ontologies = __get_stored_ontologies(ontology_folder=ontology_folder, catalog_file_path=catalog_file_path)
    __close_imports(ontology=merged_ontology, stored_ontologies=stored_ontologies, imported_ontologies=set())
    merged_ontology.commit()
    merged_ontology.namespace_manager.reset()
    merged_ontology.serialize(destination=merged_ontology_file_path)
    merged_ontology.close()
    


merge(
    ontology_folder='/Users/pawel.garbacz/Documents/edmc/github/edmc/tools/resources/idmp',
    ontology_file_path='../resources/idmp/ISO/ISO11238-Substances.rdf',
    catalog_file_path='../resources/idmp/catalog-v001.xml',
    merged_ontology_file_path='../resources/idmp/ISO/ISO11238-Substances-Merged.ttl')
