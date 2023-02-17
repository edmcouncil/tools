from shacl.objects.shacl_model_attribute import ShaclModelAttribute
from shacl.objects.shacl_model_node import ShaclModelNode
from shacl.objects.shacl_model_property import ShaclModelProperty
from shacl.objects.shacl_severity import ShaclSeverity


class ShaclModelRestriction(ShaclModelAttribute):
    def __init__(self, property: ShaclModelProperty, range: ShaclModelNode, severity: ShaclSeverity):
        super().__init__(severity=severity, property=property)
        self.range = range