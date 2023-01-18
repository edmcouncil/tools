from shacl.objects.shacl_model_node import ShaclModelNode
from shacl.objects.shacl_model_property import ShaclModelProperty
from shacl.objects.shacl_model_restriction import ShaclModelRestriction
from shacl.objects.shacl_severity import ShaclSeverity


class ShaclModelValueRestriction(ShaclModelRestriction):
    def __init__(self, property: ShaclModelProperty, range: ShaclModelNode, severity: ShaclSeverity):
        super().__init__(property=property, range=range, severity=severity)
