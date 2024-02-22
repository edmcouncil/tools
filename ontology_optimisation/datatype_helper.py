import re

from rdflib import *

ontology = Graph()
ontology.parse('dev.fibo-quickstart.ttl')
for (subject, predicate, object) in ontology:
    if isinstance(object, Literal):
        if object.datatype == XSD.dateTime:
            datetime = str(object.value)
            if '.' in datetime and datetime[-1] == '0':
                print(subject, '|', predicate, '|', object)
        
# with open('dev.fibo-quickstart.ttl') as file:
#     text = file.read()
#
# pattern = re.compile(r'".+\.\d+0+"\^\^xsd:dateTime')
# matches = pattern.findall(string=text)
# for match in matches:
#     print(match)