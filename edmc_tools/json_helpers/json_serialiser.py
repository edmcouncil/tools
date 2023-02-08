import json
import os

import pandas


def save_list_of_dicts_as_json_file(dicts: list, output_folder: str, json_file_name: str):
    dict_as_json = json.dumps(dicts, indent=4)
    dict_as_json_file_name = os.path.join(output_folder, json_file_name)
    os.makedirs(os.path.dirname(dict_as_json_file_name), exist_ok=True)
    json_file = open(dict_as_json_file_name, mode='w')
    json_file.write(dict_as_json)
    json_file.close()
    
    
def save_list_of_dicts_as_table_file(dicts: list, output_folder: str, table_file_name: str, column_to_explode: str, column_to_copy: str):
    dict_dataframes = list()
    for dict in dicts:
        dict_as_dataframe = pandas.json_normalize(dict)
        if column_to_explode in dict_as_dataframe.columns:
            dict_as_dataframe = dict_as_dataframe.explode(column=column_to_explode, ignore_index=True)
            dict_as_dataframe_normalised = pandas.json_normalize(dict_as_dataframe[column_to_explode])
            dict_as_dataframe_normalised.insert(0, column_to_copy, dict_as_dataframe[column_to_copy])
            dict_dataframes.append(dict_as_dataframe_normalised)
    dicts_dataframe = pandas.concat(dict_dataframes)
    dict_as_table_file_name = os.path.join(output_folder, table_file_name)
    os.makedirs(os.path.dirname(dict_as_table_file_name), exist_ok=True)
    dicts_dataframe.to_excel(dict_as_table_file_name, index=False)
    
    
def save_dict_as_table_file(dict_to_be_saved: dict, output_folder: str, table_file_name: str, columns_to_be_expanded: list):
    dict_as_dataframe = pandas.json_normalize(dict_to_be_saved)
    for column_to_be_expanded in columns_to_be_expanded:
        if column_to_be_expanded in dict_as_dataframe.columns:
            dict_as_dataframe = dict_as_dataframe.explode(column=column_to_be_expanded, ignore_index=True)
    dict_as_table_file_name = os.path.join(output_folder, table_file_name)
    os.makedirs(os.path.dirname(dict_as_table_file_name), exist_ok=True)
    dict_as_dataframe.to_excel(dict_as_table_file_name, index=False)