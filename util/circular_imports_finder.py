import os

from networkx import Graph, simple_cycles, DiGraph
from rdflib import Graph as OWLGraph, OWL

from util.ontology_collector import get_local_ontology_map


def populate_imports_graph(ontology: OWLGraph, import_graph: DiGraph, local_ontology_map: dict, parsed_ontology_iris: set, ontology_folder_root: str):
    owl_imports = set(ontology.subject_objects(predicate=OWL.imports))
    for owl_import in owl_imports:
        importing_ontology_iri = str(owl_import[0])
        imported_ontology_iri = str(owl_import[1])
        import_graph.add_edge(importing_ontology_iri, imported_ontology_iri)
        if imported_ontology_iri not in parsed_ontology_iris:
            imported_ontology = OWLGraph()
            try:
                imported_ontology.parse(os.path.join(ontology_folder_root, local_ontology_map[imported_ontology_iri]))
            except:
                try:
                    imported_ontology.parse(imported_ontology_iri)
                except Exception as exception:
                    print('Was not able to import', imported_ontology_iri)
            parsed_ontology_iris.add(imported_ontology_iri)
            print(imported_ontology_iri)
            populate_imports_graph(
                ontology=imported_ontology,
                import_graph=import_graph,
                local_ontology_map=local_ontology_map,
                parsed_ontology_iris=parsed_ontology_iris,
                ontology_folder_root=ontology_folder_root)


def find_circular_imports_in_ontology(ontology_file_path: str, ontology_catalog_path: str, ontology_folder_root: str):
    import_graph = DiGraph()
    ontology = OWLGraph()
    local_ontology_map = get_local_ontology_map(ontology_catalog_path=ontology_catalog_path)
    ontology.parse(ontology_file_path)
    populate_imports_graph(
        ontology=ontology,
        import_graph=import_graph,
        local_ontology_map=local_ontology_map,
        parsed_ontology_iris=set(),
        ontology_folder_root=ontology_folder_root)
    import_cycles = list(simple_cycles(import_graph))
    print(import_cycles)
    
find_circular_imports_in_ontology(
    ontology_file_path='/Users/pawel.garbacz/idmp/AboutIDMPDev-ReferenceIndividuals.rdf',
    ontology_catalog_path='/Users/pawel.garbacz/idmp/catalog-v001.xml',
    ontology_folder_root='/Users/pawel.garbacz/idmp/')
    