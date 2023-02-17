from shacl.objects.shacl_model_node import ShaclModelNode
from shacl.objects.shacl_model_property import ShaclModelProperty
from shacl.objects.shacl_severity import ShaclSeverity


class ShaclModelAttribute(ShaclModelNode):
    def __init__(self, severity: ShaclSeverity, property: ShaclModelProperty=None):
        self.severity = severity
        self.property = property