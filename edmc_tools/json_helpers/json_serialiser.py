import json
import os

import pandas


def save_dict_as_json_file(dicts: list, output_folder: str, json_file_name: str):
    dict_as_json = json.dumps(dicts, indent=4)
    dict_as_json_file_name = os.path.join(output_folder, json_file_name)
    os.makedirs(os.path.dirname(dict_as_json_file_name), exist_ok=True)
    json_file = open(dict_as_json_file_name, mode='w')
    json_file.write(dict_as_json)
    json_file.close()
    
    
def save_dict_as_table_file(dicts: list, output_folder: str, table_file_name: str):
    dict_as_dataframe = pandas.json_normalize(dicts)
    dict_as_table_file_name = os.path.join(output_folder, table_file_name)
    os.makedirs(os.path.dirname(dict_as_table_file_name), exist_ok=True)
    dict_as_dataframe.to_excel(dict_as_table_file_name, index=False)