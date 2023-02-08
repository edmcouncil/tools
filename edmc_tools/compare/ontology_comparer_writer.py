from compare.common import *
from json_helpers.json_serialiser import save_list_of_dicts_as_json_file, save_list_of_dicts_as_table_file, \
    save_dict_as_table_file

DIFF_RESOURCES_JSON_FILE_NAME = 'different_resources_in_ontology_revisions.json'
DIFF_AXIOMS_JSON_FILE_NAME = 'different_axioms_for_same_subjects.json'
DIFF_ONTOLOGIES_JSON_FILE_NAME = 'different_ontologies_in_repository_versions.json'
DIFF_RESOURCES_EXCEL_FILE_NAME = 'different_resources_in_ontology_revisions.xlsx'
DIFF_AXIOMS_EXCEL_FILE_NAME = 'different_axioms_for_same_subjects.xlsx'
DIFF_ONTOLOGIES_EXCEL_FILE_NAME = 'different_ontologies_in_repository_versions.xlsx'


def save_diff_dicts(
        comparison_prefix: str,
        left_revision_id: str,
        right_revision_id: str,
        output_folder: str,
        diff_ontologies_dict: dict,
        diff_resource_dicts_list: list,
        diff_axioms_for_same_subjects_dicts_list: list):
    save_list_of_dicts_as_json_file(
        dicts=diff_resource_dicts_list,
        output_folder=output_folder,
        json_file_name=comparison_prefix + '_' + DIFF_RESOURCES_JSON_FILE_NAME)
    save_list_of_dicts_as_table_file(
        dicts=diff_resource_dicts_list,
        output_folder=output_folder,
        table_file_name=comparison_prefix + '_' + DIFF_RESOURCES_EXCEL_FILE_NAME,
        column_to_explode=ONTOLOGY_DIFF_KEY,
        column_to_copy=ONTOLOGY_NAME_KEY)
    
    save_list_of_dicts_as_json_file(
        dicts=diff_axioms_for_same_subjects_dicts_list,
        output_folder=output_folder,
        json_file_name=comparison_prefix + '_' + DIFF_AXIOMS_JSON_FILE_NAME)
    save_list_of_dicts_as_table_file(
        dicts=diff_axioms_for_same_subjects_dicts_list,
        output_folder=output_folder,
        table_file_name=comparison_prefix + '_' + DIFF_AXIOMS_EXCEL_FILE_NAME,
        column_to_explode=ONTOLOGY_DIFF_KEY,
        column_to_copy=ONTOLOGY_NAME_KEY)
    
    save_list_of_dicts_as_json_file(
        dicts=[diff_ontologies_dict],
        output_folder=output_folder,
        json_file_name=comparison_prefix + '_' + DIFF_ONTOLOGIES_JSON_FILE_NAME)
    column_1 = \
        get_specific_constant(
            constant=ONTOLOGIES_LEFT_BUT_NOT_RIGHT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    column_2 = \
        get_specific_constant(
            constant=ONTOLOGIES_RIGHT_BUT_NOT_LEFT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    save_dict_as_table_file(
        dict_to_be_saved=diff_ontologies_dict,
        output_folder=output_folder,
        table_file_name=comparison_prefix + '_' + DIFF_ONTOLOGIES_EXCEL_FILE_NAME,
        columns_to_be_expanded = [column_1, column_2])
