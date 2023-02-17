from rdflib import Graph, RDF, OWL, URIRef, RDFS

from shacl.data_model_class_generator import generate_model_class_from_owl_class_with_attributes
from shacl.objects.shacl_model_identified_class import ShaclModelIdentifiedClass
from shacl.objects.shacl_model_individual import ShaclModelIndividual
from shacl.objects.shacl_model_property import ShaclModelProperty
from shacl.resource_recognizer import if_resource_is_datatype


def generate_shacl_model_from_ontology(ontology: Graph):
    generate_data_properties_from_owl_properties(ontology=ontology)
    generate_data_classes_from_owl_classes(ontology=ontology)
    generate_data_individuals_from_owl_individuals(ontology=ontology)


def generate_data_classes_from_owl_classes(ontology: Graph):
    owl_classes = list(ontology.subjects(predicate=RDF.type, object=OWL.Class))
    for owl_class in owl_classes:
        if isinstance(owl_class, URIRef):
            is_datatype = if_resource_is_datatype(resource=owl_class)
            generate_model_class_from_owl_class_with_attributes(owl_class=owl_class, ontology=ontology, is_datatype=is_datatype)
            
    for shacl_model_class in ShaclModelIdentifiedClass.registry.values():
        owl_super_classes = set(ontology.transitive_objects(subject=shacl_model_class.iri, predicate=RDFS.subClassOf))
        owl_super_classes.add(OWL.Thing)
        if shacl_model_class.iri in owl_super_classes:
            owl_super_classes.remove(shacl_model_class.iri)
        for owl_super_class in owl_super_classes:
            if isinstance(owl_super_class, URIRef):
                super_class = ShaclModelIdentifiedClass.registry[owl_super_class]
                shacl_model_class.super_classes.add(super_class)
                super_class.is_leaf = False
            
    for shacl_model_class in ShaclModelIdentifiedClass.registry.values():
        shacl_model_class.inherit_attributes_from_super_classes()
     

def generate_data_properties_from_owl_properties(ontology: Graph):
    owl_object_properties = list(ontology.subjects(predicate=RDF.type, object=OWL.ObjectProperty))
    for owl_object_property in owl_object_properties:
        if isinstance(owl_object_property, URIRef):
            generate_data_property_from_owl_property(owl_property=owl_object_property, ontology=ontology)
    
    owl_datatype_properties = list(ontology.subjects(predicate=RDF.type, object=OWL.DatatypeProperty))
    for owl_datatype_property in owl_datatype_properties:
        if isinstance(owl_datatype_property, URIRef):
            generate_data_property_from_owl_property(owl_property=owl_datatype_property, ontology=ontology)
    
    for data_property in ShaclModelProperty.registry.values():
        data_property.add_superproperties()


def generate_data_property_from_owl_property(owl_property: URIRef, ontology: Graph):
    ShaclModelProperty(iri=owl_property, ontology=ontology, super_properties=set())


def generate_data_individuals_from_owl_individuals(ontology: Graph):
    owl_individuals = list(ontology.subjects(predicate=RDF.type, object=OWL.NamedIndividual))
    for owl_individual in owl_individuals:
        if isinstance(owl_individual, URIRef):
            generate_data_individual_from_owl_individual(owl_individual=owl_individual, ontology=ontology)
    
        
def generate_data_individual_from_owl_individual(owl_individual: URIRef, ontology: Graph):
    owl_types = list(ontology.objects(subject=owl_individual, predicate=RDF.type))
    types = set()
    for owl_type in owl_types:
        if owl_type == OWL.NamedIndividual:
            continue
        if owl_type in ShaclModelIdentifiedClass.registry:
            type = ShaclModelIdentifiedClass.registry[owl_type]
        else:
            type = generate_model_class_from_owl_class_with_attributes(owl_class=owl_type, ontology=ontology, is_datatype=False)
        types.add(type)
    ShaclModelIndividual(iri=owl_individual,types=types)
    