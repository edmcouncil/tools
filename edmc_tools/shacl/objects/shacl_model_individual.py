from rdflib import URIRef

from shacl.objects.shacl_model_resource import ShaclModelResource


class ShaclModelIndividual(ShaclModelResource):
    registry = dict()
    
    def __init__(self, iri: URIRef, types: set):
        super().__init__(iri)
        self.types = types
        ShaclModelIndividual.registry[iri] = self
        