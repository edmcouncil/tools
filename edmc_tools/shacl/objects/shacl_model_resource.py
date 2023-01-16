from rdflib.term import Identifier

from shacl.objects.shacl_model_node import ShaclModelNode


class ShaclModelResource(ShaclModelNode):
    registry = dict()
    
    def __init__(self, iri: Identifier):
        self.iri = iri
        self.bracket_iri = '<' + str(self.iri) + '>'
        ShaclModelResource.registry[iri] = self