from compare.common import *
from compare.comparison_config import ComparisonConfig
from json_helpers.json_serialiser import save_list_of_dicts_as_json_file, \
    save_list_of_dicts_as_excel_file_with_one_sheet, \
    save_dict_as_excel_file, save_list_of_dicts_as_excel_file_with_two_sheets

DIFF_RESOURCES_JSON_FILE_NAME = 'different_resources_in_ontology_revisions.json'
DIFF_AXIOMS_JSON_FILE_NAME = 'different_axioms_for_same_subjects.json'
DIFF_ONTOLOGIES_JSON_FILE_NAME = 'different_ontologies_in_repository_versions.json'
DIFF_RESOURCES_EXCEL_FILE_NAME = 'different_resources_in_ontology_revisions.xlsx'
DIFF_AXIOMS_EXCEL_FILE_NAME = 'different_axioms_for_same_subjects.xlsx'
DIFF_ONTOLOGIES_EXCEL_FILE_NAME = 'different_ontologies_in_repository_versions.xlsx'


def save_deltas(
        comparison_prefix: str,
        left_revision_id: str,
        right_revision_id: str,
        output_folder: str,
        diff_ontologies_dict: dict,
        diff_resource_dicts_list: list,
        diff_axioms_for_same_subjects_dicts_list: list,
        config: ComparisonConfig):
    ontologies_comparison_first_aspect = \
        get_specific_constant(
            constant=ONTOLOGIES_LEFT_BUT_NOT_RIGHT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    ontologies_comparison_second_aspect = \
        get_specific_constant(
            constant=ONTOLOGIES_RIGHT_BUT_NOT_LEFT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    save_list_of_dicts_as_json_file(
        dicts=[diff_ontologies_dict],
        output_folder=output_folder,
        json_file_name=comparison_prefix + '_' + DIFF_ONTOLOGIES_JSON_FILE_NAME)
    save_dict_as_excel_file(
        dict_to_be_saved=diff_ontologies_dict,
        output_folder=output_folder,
        table_file_name=comparison_prefix + '_' + DIFF_ONTOLOGIES_EXCEL_FILE_NAME,
        columns_to_be_expanded=[ontologies_comparison_first_aspect, ontologies_comparison_second_aspect])

    save_list_of_dicts_as_json_file(
        dicts=diff_resource_dicts_list,
        output_folder=output_folder,
        json_file_name=comparison_prefix + '_' + DIFF_RESOURCES_JSON_FILE_NAME)
    if config.verbose:
        resources_comparison_first_aspect = \
            get_specific_constant(
                constant=RESOURCES_LEFT_BUT_NOT_RIGHT,
                left_specific=left_revision_id,
                right_specific=right_revision_id)
        resources_comparison_second_aspect = \
            get_specific_constant(
                constant=RESOURCES_RIGHT_BUT_NOT_LEFT,
                left_specific=left_revision_id,
                right_specific=right_revision_id)
        save_list_of_dicts_as_excel_file_with_two_sheets(
            dicts=diff_resource_dicts_list,
            output_folder=output_folder,
            table_file_name=comparison_prefix + '_' + DIFF_RESOURCES_EXCEL_FILE_NAME,
            column_to_explode=ONTOLOGY_DIFF_KEY,
            column_to_copy=ONTOLOGY_NAME_KEY,
            first_aspect=resources_comparison_first_aspect,
            second_aspect=resources_comparison_second_aspect)
    else:
        save_list_of_dicts_as_excel_file_with_one_sheet(
            dicts=diff_resource_dicts_list,
            output_folder=output_folder,
            table_file_name=comparison_prefix + '_' + DIFF_RESOURCES_EXCEL_FILE_NAME,
            column_to_explode=ONTOLOGY_DIFF_KEY,
            column_to_copy=ONTOLOGY_NAME_KEY)
    
    save_list_of_dicts_as_json_file(
        dicts=diff_axioms_for_same_subjects_dicts_list,
        output_folder=output_folder,
        json_file_name=comparison_prefix + '_' + DIFF_AXIOMS_JSON_FILE_NAME)
    
    if not config.verbose:
        save_list_of_dicts_as_excel_file_with_one_sheet(
            dicts=diff_axioms_for_same_subjects_dicts_list,
            output_folder=output_folder,
            table_file_name=comparison_prefix + '_' + DIFF_AXIOMS_EXCEL_FILE_NAME,
            column_to_explode=ONTOLOGY_DIFF_KEY,
            column_to_copy=ONTOLOGY_NAME_KEY)
    
    
