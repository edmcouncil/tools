from rdflib import URIRef, XSD


def if_resource_is_datatype(resource: URIRef) -> bool:
    return resource in XSD
