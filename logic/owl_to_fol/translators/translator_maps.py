from rdflib import XSD, OWL

SW_TO_PYTHON_DATATYPE_MAP = \
    {
        XSD.int : int,
        XSD.integer: int,
        XSD.negativeInteger: int,
        XSD.nonPositiveInteger: int,
        XSD.positiveInteger: int,
        XSD.nonNegativeInteger: int,
        XSD.decimal: float,
        XSD.float: float,
        OWL.rational: float,
        OWL.real: float
    }