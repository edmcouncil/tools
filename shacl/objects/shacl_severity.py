from enum import Enum

from rdflib import SH


class ShaclSeverity(Enum):
    NOT_SET = ''
    INFO = SH.Info
    WARNING = SH.Warning
    VIOLATION = SH.Violation