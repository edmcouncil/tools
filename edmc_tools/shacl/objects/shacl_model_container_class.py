from shacl.objects.shacl_model_node import ShaclModelNode


class ShaclModelContainerClass(ShaclModelNode):
    def __init__(self, complexity_type: str=None, constituting_entities: set = None):
        super().__init__()
        self.constituting_attributes = constituting_entities
        self.complexity_type = complexity_type
