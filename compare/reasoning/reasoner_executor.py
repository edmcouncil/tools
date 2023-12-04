import json
import subprocess
import time
import os

import pandas
from rdflib import Graph
from tqdm import tqdm


def run_reasoner_over_folder(folder_path: str):
    with open(os.path.join(folder_path, 'ontologies_register.json')) as commit_id_file:
        consolidated_ontologies_register = json.load(commit_id_file)
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
    for commit_id_file in tqdm(os.listdir(folder_path), desc='reasoner runs'):
        if commit_id_file.endswith(".ttl"):
            file_path = os.path.join(folder_path, commit_id_file)
            file_name = commit_id_file.split('.')[0]
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
            commit_id = commit_id_file.replace('.ttl', '')
            reasoning_times_register[commit_id] = reasoning_time
    consolidated_ontologies_register_dataframe = pandas.DataFrame.from_dict(data=consolidated_ontologies_register, orient='index')
    reasoning_times_dataframe = pandas.DataFrame.from_dict(data=reasoning_times_register, orient='index')
    consolidated_ontologies_register_dataframe.reset_index(inplace=True)
    consolidated_ontologies_register_dataframe.columns = ['commit_id', 'commit_date']
    reasoning_times_dataframe.reset_index(inplace=True)
    reasoning_times_dataframe.columns = ['commit_id', 'reasoning_time']
    reasoning_times_register_dataframe = reasoning_times_dataframe.merge(right=consolidated_ontologies_register_dataframe)
    reasoning_times_register_dataframe.reset_index(inplace=True)
    reasoning_times_register_dataframe.to_excel(os.path.join(folder_path, 'ontology_reasoning_times.xlsx'), index=False)
    