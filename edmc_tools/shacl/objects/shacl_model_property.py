from rdflib import URIRef, Graph, RDFS

from shacl.objects.shacl_model_resource import ShaclModelResource


class ShaclModelProperty(ShaclModelResource):
    registry = dict()
    
    def add_superproperties(self):
        owl_super_properties = set(self.ontology.transitive_objects(predicate=RDFS.subPropertyOf, subject=self.iri))
        if self.iri in owl_super_properties:
            owl_super_properties.remove(self.iri)
        for owl_super_property in owl_super_properties:
            self.super_properties.add(ShaclModelProperty.registry[owl_super_property])
    
    def __init__(self, iri: URIRef, super_properties: set, ontology: Graph):
        super().__init__(iri)
        self.super_properties = super_properties
        self.ontology = ontology
        ShaclModelProperty.registry[iri] = self
        
        
    