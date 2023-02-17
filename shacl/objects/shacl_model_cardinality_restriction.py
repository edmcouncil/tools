from shacl.objects.shacl_model_cardinality import ShaclModelCardinality
from shacl.objects.shacl_model_node import ShaclModelNode
from shacl.objects.shacl_model_property import ShaclModelProperty
from shacl.objects.shacl_model_restriction import ShaclModelRestriction
from shacl.objects.shacl_severity import ShaclSeverity


class ShaclModelCardinalityRestriction(ShaclModelRestriction):
    def __init__(self, property: ShaclModelProperty, range: ShaclModelNode, cardinality: ShaclModelCardinality, severity: ShaclSeverity):
        super().__init__(property=property, range=range, severity=severity)
        self.cardinality = cardinality