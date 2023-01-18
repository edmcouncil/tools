from rdflib import Literal

from shacl.objects.shacl_model_node import ShaclModelNode


class ShaclModelLiteral(ShaclModelNode):
    registry = dict()
    
    def __init__(self, value: Literal):
        self.value = value
        ShaclModelLiteral.registry[value] = self
        
    def __str__(self):
        return str(self.value)