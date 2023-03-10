from rdflib.term import Identifier

from shacl.objects.shacl_model_node import ShaclModelNode


class ShaclModelResource(ShaclModelNode):
    registry = dict()
    
    def __init__(self, iri: Identifier):
        self.iri = iri
        ShaclModelResource.registry[iri] = self
    
    def __str__(self):
        return ' '.join([str(self.iri)])
    
    def __repr__(self):
        return ' '.join([str(self.iri)])