from rdflib.term import Identifier

from shacl.objects.shacl_model_individual import ShaclModelIndividual
from shacl.objects.shacl_model_resource import ShaclModelResource


class ShaclModelIdentifiedClass(ShaclModelResource):
    registry = dict()
    
    def __init__(self, iri: Identifier, attributes: set, super_classes: set, is_leaf=True, is_datatype=False):
        super().__init__(iri)
        self.attributes = attributes
        self.super_classes = super_classes
        self.is_datatype = is_datatype
        self.is_leaf = is_leaf
        ShaclModelIdentifiedClass.registry[iri] = self
        
    def inherit_attributes_from_super_classes(self):
        for super_class in self.super_classes:
            self.__inherit_attributes_from_super_class(super_class=super_class)
        self.__remove_obsolete_attributes()
    
    def __inherit_attributes_from_super_class(self, super_class):
        super_class.inherit_attributes_from_super_classes()
        self.attributes = self.attributes.union(super_class.attributes)
        
    def __remove_obsolete_attributes(self):
        non_obsolete_attributes = self.attributes.copy()
        for attribute_1 in self.attributes:
            if not hasattr(attribute_1, 'cardinality'):
                continue
            attribute_property_1 = attribute_1.property
            attribute_range_1 = attribute_1.range
            attribute_cardinality_1 = attribute_1.cardinality
            for attribute_2 in self.attributes:
                if not hasattr(attribute_2, 'cardinality'):
                    continue
                attribute_property_2 = attribute_2.property
                attribute_range_2 = attribute_2.range
                attribute_cardinality_2 = attribute_2.cardinality
                if not attribute_1 == attribute_2:
                    if attribute_property_1 == attribute_property_2 or attribute_property_1 in attribute_property_2.super_properties:
                        parents = set()
                        if isinstance(attribute_range_2, ShaclModelIdentifiedClass):
                            parents = attribute_range_2.super_classes
                        if isinstance(attribute_range_2, ShaclModelIndividual):
                            parents = attribute_range_2.types
                        if attribute_range_1 == attribute_range_2 or attribute_range_1 in parents:
                            if attribute_cardinality_2.min <= attribute_cardinality_1.min or attribute_cardinality_2.max >= attribute_cardinality_1.max:
                                if attribute_1 in non_obsolete_attributes:
                                    non_obsolete_attributes.remove(attribute_1)
        self.attributes = non_obsolete_attributes
        