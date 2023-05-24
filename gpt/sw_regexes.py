import re

from rdflib import OWL

owl_class_prefix_desc_regex = re.compile(pattern=r'[a-z\-]+:\w+\s*a\s+owl:Class.+?\.\n', flags=re.DOTALL)
owl_class_nonprefix_desc_regex = re.compile(pattern=r'(<([^\s]+)>\s+rdf:type\s+owl:Class.+?\.\n)', flags=re.DOTALL)
label_regex = re.compile(pattern=r'rdfs:label\s+"(.+?)"')
def_regex = re.compile(pattern=r'skos:definition\s+"(.+?)"')
ex_regex = re.compile(pattern=r'skos:example\s+(.+?)"', flags=re.DOTALL)
notes_regex = re.compile(pattern=r'fibo-fnd-utl-av:explanatoryNote.+?"(.+?)"', flags=re.DOTALL)
prefix_regex = re.compile(pattern=r'[a-z\-]+:')
isDefinedBy_regex = re.compile(pattern=r'rdfs:isDefinedBy\s+[a-z\-]+:\s+;', flags=re.DOTALL)
isDefinedIn_regex = re.compile(pattern=r'fibo-fnd-rel-rel:isDefinedIn\s+.+?;', flags=re.DOTALL)

REGEX_MAP = {OWL.Class: owl_class_nonprefix_desc_regex}
