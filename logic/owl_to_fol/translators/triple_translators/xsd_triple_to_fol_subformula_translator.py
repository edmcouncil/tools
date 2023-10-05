from rdflib import URIRef, XSD

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.constant_term import ConstantTerm
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.predicate import ARITHMETIC_LESS_PREDICATE, ARITHMETIC_GREATER_PREDICATE, Predicate, \
    ARITHMETIC_LESSEQ_PREDICATE, ARITHMETIC_GREATEREQ_PREDICATE
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.translator_maps import SW_TO_PYTHON_DATATYPE_MAP


def translate_xsd_construct_to_fol_subformula(rdf_predicate: URIRef, sw_arguments: list, variables: list) -> Formula:
    match rdf_predicate:
        case XSD.minExclusive: return __translate_restriction(sw_arguments=sw_arguments, variables=variables, restricting_predicate=ARITHMETIC_LESS_PREDICATE)
        case XSD.maxExclusive: return __translate_restriction(sw_arguments=sw_arguments, variables=variables, restricting_predicate=ARITHMETIC_GREATER_PREDICATE)
        case XSD.minInclusive: return __translate_restriction(sw_arguments=sw_arguments, variables=variables, restricting_predicate=ARITHMETIC_GREATEREQ_PREDICATE)
        case XSD.maxInclusive: return __translate_restriction(sw_arguments=sw_arguments, variables=variables, restricting_predicate=ARITHMETIC_LESSEQ_PREDICATE)
        
        
def __translate_restriction(sw_arguments: list, variables: list, restricting_predicate: Predicate) -> Formula:
    sw_restriction = sw_arguments[0]
    sw_datatype_literal = sw_arguments[1]
    sw_datatype = sw_datatype_literal.datatype
    if sw_datatype in SW_TO_PYTHON_DATATYPE_MAP:
        sw_restricting_value = sw_datatype_literal.value
        sw_restricting_value_type = SW_TO_PYTHON_DATATYPE_MAP[sw_datatype]
    else:
        sw_restricting_value = str(sw_datatype_literal.value)
        sw_restricting_value_type = str
    formula = \
        AtomicFormula(
            predicate=restricting_predicate,
            arguments=[variables[0], ConstantTerm(origin_value=sw_restricting_value, origin_type=sw_restricting_value_type)],
            tptp_type='tff')
    FormulaOriginRegistry.sw_to_fol_map[sw_restriction] = formula
    return formula
