from shacl.objects.shacl_model_node import ShaclModelNode


class ShaclModelCollection(ShaclModelNode):
    def __init__(self, complexity_type: str = str(), collected_nodes: set = None):
        super().__init__()
        self.collected_nodes = collected_nodes
        self.complexity_type = complexity_type
        
    def __str__(self):
        collected_node_strings = list()
        for node in self.collected_nodes:
            collected_node_strings.append(str(node))
        return ' '.join([str(self.complexity_type)] + ['collecting'] + collected_node_strings)
