import json
import subprocess
import time
import os

import pandas
from rdflib import Graph


def run_reasoner_over_folder(folder_path: str):
    with open(os.path.join(folder_path, 'ontologies_register.json')) as file:
        consolidated_ontologies_register = json.load(file)
    empty_ontology = Graph()
    empty_ontology_file_path = os.path.join(folder_path,'empty.ttl')
    empty_ontology.serialize(empty_ontology_file_path)
    empty_ontology_output_file_path = os.path.join(folder_path, 'empty_consistency.txt')
    start = time.time()
    reasoning_process = \
        subprocess.Popen(
            "java -jar ./onto-viewer-toolkit.jar --goal consistency-check --data " + empty_ontology_file_path + " --output " + empty_ontology_output_file_path,
            shell=True)
    reasoning_process.wait()
    end = time.time()
    empty_ontology_reasoning_time = end - start
    os.remove(empty_ontology_file_path)
    reasoning_times_register = dict()
    for file in os.listdir(folder_path):
        if file.endswith(".ttl"):
            file_path = os.path.join(folder_path, file)
            file_name = file.split('.')[0]
            output_file_path = os.path.join(folder_path, file_name + "_consistency.txt")
            start = time.time()
            reasoning_process = \
                subprocess.Popen(
                    "java -jar ./onto-viewer-toolkit.jar --goal consistency-check --data " + file_path + " --output " + output_file_path,
                    shell=True)
            try:
                reasoning_process.wait(timeout=300)
            except subprocess.TimeoutExpired as exception:
                print(exception.output)
                reasoning_time = 300
            else:
                end = time.time()
                reasoning_time = (end - start) - empty_ontology_reasoning_time
            reasoning_time_datetime = consolidated_ontologies_register[file_name]
            reasoning_times_register[reasoning_time_datetime] = reasoning_time
    reasoning_times_dataframe = pandas.DataFrame.from_dict(data=reasoning_times_register, orient='index')
    reasoning_times_dataframe.reset_index(inplace=True)
    reasoning_times_dataframe.columns = ['time_stamp', 'time_length']
    reasoning_times_dataframe.to_excel(os.path.join(folder_path, 'ontology_reasoning_times.xlsx'), index=False)
    