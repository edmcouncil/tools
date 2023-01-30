from json_helpers.json_serialiser import save_dict_as_json_file

DIFF_RESOURCES_JSON_FILE_NAME = 'different_resources.json'
DIFF_AXIOMS_JSON_FILE_NAME = 'different_axioms_for_same_subjects.json'
DIFF_ONTOLOGIES_JSON_FILE_NAME = 'different_ontologies.json'
DIFF_RESOURCES_EXCEL_FILE_NAME = 'different_resources.xlsx'
DIFF_AXIOMS_EXCEL_FILE_NAME = 'different_axioms_for_same_subjects.xlsx'
DIFF_ONTOLOGIES_EXCEL_FILE_NAME = 'different_ontologies.xlsx'


def save_diff_dicts(comparison_prefix: str, output_folder: str, diff_ontologies_list: list,diff_resource_dicts_list: list, diff_axioms_for_same_subjects_dicts_list: list):
    save_dict_as_json_file(
        dicts=diff_resource_dicts_list,
        output_folder=output_folder,
        json_file_name=comparison_prefix + '_' + DIFF_RESOURCES_JSON_FILE_NAME)
    # save_dict_as_table_file(
    #     dicts=diff_resource_dicts_list,
    #     output_folder=output_folder,
    #     table_file_name=comparison_prefix + '_' + DIFF_RESOURCES_EXCEL_FILE_NAME,
    #     columns_to_explode=list())
    
    save_dict_as_json_file(
        dicts=diff_axioms_for_same_subjects_dicts_list,
        output_folder=output_folder,
        json_file_name=comparison_prefix + '_' + DIFF_AXIOMS_JSON_FILE_NAME)
    # save_dict_as_table_file(
    #     dicts=diff_axioms_for_same_subjects_dicts_list,
    #     output_folder=output_folder,
    #     table_file_name=comparison_prefix + '_' + DIFF_AXIOMS_EXCEL_FILE_NAME,
    #     columns_to_explode=list())
    
    save_dict_as_json_file(
        dicts=diff_ontologies_list,
        output_folder=output_folder,
        json_file_name=comparison_prefix + '_' + DIFF_ONTOLOGIES_JSON_FILE_NAME)
    # save_dict_as_table_file(
    #     dicts=diff_ontologies_list,
    #     output_folder=output_folder,
    #     table_file_name=comparison_prefix + '_' + DIFF_ONTOLOGIES_EXCEL_FILE_NAME,
    #     columns_to_explode=[LEFT_BUT_NOT_RIGHT, RIGHT_BUT_NOT_LEFT])
