import argparse
import logging

from rdflib import Graph, RDF, OWL, URIRef, RDFS
from tqdm import tqdm


def impose_disjointness(ontology_input_path: str, ontology_output_path: str, ignored_namespace='https://www.omg.org/spec/Commons/'):
    input_ontology = Graph()
    input_ontology.parse(ontology_input_path)
    output_ontology = Graph() + input_ontology
    
    owl_classes = set(input_ontology.subjects(predicate=RDF.type, object=OWL.Class))
    possible_disjoint_class_tuples = set()
    logging.info(msg='Find all possibly disjoint classes')
    for class_1 in tqdm(owl_classes):
        if isinstance(class_1, URIRef):
            if not str(class_1).startswith(ignored_namespace):
                iri_namespace_1 = __get_namespace_for_iri(iri=class_1)
                for class_2 in owl_classes:
                    if not class_1 == class_2:
                        if isinstance(class_2, URIRef):
                            if not str(class_1).startswith(ignored_namespace):
                                iri_namespace_2 = __get_namespace_for_iri(iri=class_2)
                                if (not class_1 == class_2) and iri_namespace_1 == iri_namespace_2:
                                    instances_1 = __get_all_instances_for_class(ontology=input_ontology, iri_class=class_1)
                                    instances_2 = __get_all_instances_for_class(ontology=input_ontology, iri_class=class_2)
                                    if len(instances_1) > 0 and len(instances_2) > 0 and len(instances_1.intersection(instances_2)) == 0:
                                        if (class_2, class_1) not in possible_disjoint_class_tuples:
                                            if not (class_1, OWL.disjointWith, class_2) in input_ontology and not (class_2, OWL.disjointWith, class_1) in input_ontology:
                                                possible_disjoint_class_tuples.add((class_1, class_2))
    
    logging.info(msg='Find most general disjoint classes')
    disjoint_class_tuples = set()
    for possible_disjoint_class_tuple_1 in tqdm(possible_disjoint_class_tuples):
        disjoint_class_1_1 = possible_disjoint_class_tuple_1[0]
        disjoint_class_1_2 = possible_disjoint_class_tuple_1[1]
        disjoint_class_1 = disjoint_class_1_1
        disjoint_class_2 = disjoint_class_1_2
        disjoint_class_1_supertypes = __get_all_supertype_for_class(ontology=input_ontology,iri_class=disjoint_class_1)
        disjoint_class_2_supertypes = __get_all_supertype_for_class(ontology=input_ontology,iri_class=disjoint_class_2)
        drop_tuple_1 = False
        for possible_disjoint_class_tuple_2 in possible_disjoint_class_tuples:
            disjoint_class_2_1 = possible_disjoint_class_tuple_2[0]
            disjoint_class_2_2 = possible_disjoint_class_tuple_2[1]
            if disjoint_class_2_1 in disjoint_class_1_supertypes and disjoint_class_2_2 in disjoint_class_2_supertypes:
                drop_tuple_1 = True
                break
            if disjoint_class_2_1 in disjoint_class_1_supertypes and  disjoint_class_2_2 == disjoint_class_2:
                drop_tuple_1 = True
                break
            if disjoint_class_2_2 in disjoint_class_2_supertypes and disjoint_class_2_1 == disjoint_class_1:
                drop_tuple_1 = True
                break
                
            if disjoint_class_2_1 in disjoint_class_2_supertypes and disjoint_class_2_2 in disjoint_class_1_supertypes:
                drop_tuple_1 = True
                break
            if disjoint_class_2_1 in disjoint_class_2_supertypes and  disjoint_class_2_2 == disjoint_class_1:
                drop_tuple_1 = True
                break
            if disjoint_class_2_2 in disjoint_class_1_supertypes and disjoint_class_2_1 == disjoint_class_2:
                drop_tuple_1 = True
                break
        if not drop_tuple_1:
            disjoint_class_tuples.add((possible_disjoint_class_tuple_1[0], len(disjoint_class_1_supertypes),possible_disjoint_class_tuple_1[1], len(disjoint_class_2_supertypes)) )
            
    print(len(disjoint_class_tuples))
    for disjoint_class_tuple in disjoint_class_tuples:
        print(disjoint_class_tuple)
        # output_ontology.add((disjoint_class_tuple[0], OWL.disjointWith, disjoint_class_tuple[1]))
        
    output_ontology.serialize(ontology_output_path)
    input_ontology.close()
    output_ontology.close()
    
def __get_namespace_for_iri(iri: URIRef, sep='/') -> str:
    iri_parts = iri.split(sep=sep)
    iri_namespace = sep.join(iri_parts[:-1])
    return iri_namespace
    

def __get_all_instances_for_class(ontology: Graph, iri_class: URIRef) -> set:
    instances = set()
    subtypes = ontology.transitive_subjects(predicate=RDFS.subClassOf, object=iri_class)
    for subtype in subtypes:
        subtype_instances = set(ontology.subjects(predicate=RDF.type, object=subtype))
        instances = instances.union(subtype_instances)
    return instances


def __get_all_supertype_for_class(ontology: Graph, iri_class: URIRef) -> set:
    supertypes = set(ontology.transitive_objects(predicate=RDFS.subClassOf, subject=iri_class))
    supertypes.remove(iri_class)
    return supertypes
    


if __name__ == "__main__":
    # parser = argparse.ArgumentParser(description='Impose all possible disjointness axioms')
    # parser.add_argument('--input', help='Path to input ontology', metavar='IN_ONT')
    # parser.add_argument('--output', help='Path to output ontology', metavar='OUT_ONT')
    # args = parser.parse_args()
    #
    # impose_disjointness(ontology_input_path=args.input, ontology_output_path=args.output)
    
    impose_disjointness(
        ontology_input_path='../resources/idmp_quick/dev.idmp-quickstart.ttl',
        ontology_output_path='../resources/idmp_quick/dev.idmp-quickstart_disjoint_max.ttl')