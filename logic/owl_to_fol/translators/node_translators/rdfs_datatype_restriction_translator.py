import logging

from rdflib import BNode, Graph, OWL

import logic.owl_to_fol.translators.node_translators.sw_node_to_fol_translator as sw_node_to_fol_translator
from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.formula import Formula
from logic.owl_to_fol.translators.triple_translators.owl_triple_to_fol_subformula_translator import translate_oneOf


def translate_datatype_description(sw_datatype_description: BNode, rdf_graph: Graph, variables: list) -> Formula:
    formula = None
    sw_restricted_datatypes = list(rdf_graph.objects(subject=sw_datatype_description, predicate=OWL.onDatatype))
    sw_oneOfs = list(rdf_graph.objects(subject=sw_datatype_description, predicate=OWL.oneOf))
    if len(sw_restricted_datatypes) == 1:
        sw_restricted_datatype = sw_restricted_datatypes[0]
        sw_restrictions = list(rdf_graph.objects(subject=sw_datatype_description, predicate=OWL.withRestrictions))
        sw_restriction = sw_restrictions[0]
        formulae = sw_node_to_fol_translator.get_fol_formulae_from_rdf_list(rdf_list_object=sw_restriction, rdf_graph=rdf_graph, variables=variables,fol_formulae=list())
        if len(formulae) > 1:
            formula = Conjunction(arguments=formulae)
        elif len(formulae) == 1:
            formula = formulae[0]
    elif len(sw_oneOfs) == 1:
        formula = translate_oneOf(sw_arguments=[sw_datatype_description,sw_oneOfs[0]],rdf_graph=rdf_graph,variables=variables)
    else:
        logging.warning(msg='Cannot process datatype description for: ' + str(sw_datatype_description.skolemize()))
    return formula
    