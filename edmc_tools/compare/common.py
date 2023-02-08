ONTOLOGY_NAME_KEY = 'ontology'
ONTOLOGY_DIFF_KEY = 'delta'
COUNT_SUFFIX = 'count'
RESOURCES_LEFT_BUT_NOT_RIGHT = 'resources in left but not right ontology revision'
RESOURCES_RIGHT_BUT_NOT_LEFT = 'resources in right but not left ontology revision'
AXIOMS_LEFT_BUT_NOT_RIGHT = 'axioms in left but not in right ontology revision'
AXIOMS_RIGHT_BUT_NOT_LEFT = 'axioms in right but not in left ontology revision'
ONTOLOGIES_LEFT_BUT_NOT_RIGHT = 'ontologies in left but not in right repository version'
ONTOLOGIES_RIGHT_BUT_NOT_LEFT = 'ontologies in right and not in left repository version'
BOTH = 'both right and left'


def get_specific_constant(constant: str, left_specific: str, right_specific: str):
    specific_constant = constant.replace('left', left_specific)
    specific_constant = specific_constant.replace('right', right_specific)
    return specific_constant