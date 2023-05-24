from rdflib import Graph, RDFS, URIRef, OWL, RDF, XSD
from rdflib.namespace import DefinedNamespace


for xsd in dir(XSD):
    print(xsd)