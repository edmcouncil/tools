import os
import sys

from compare.ontology_comparer import compare_ontologies


def compare_ontology_folders(folder_1: str, folder_2: str, results_folder_path: str, ontology_file_extension='.rdf', verbose=False):
    both_file_paths, only_left_file_paths, only_right_file_paths = get_ontology_files(left_folder=folder_1, right_folder=folder_2)
    for ontology_path in both_file_paths:
        ontology_1_location = ontology_path[0]
        ontology_2_location = ontology_path[1]
        ontology_1_file_name, ontology_1_file_extension = os.path.splitext(ontology_1_location)
        ontology_1_file_name, ontology_2_file_extension = os.path.splitext(ontology_2_location)
        if not ontology_1_file_extension == ontology_2_file_extension:
            sys.exit(-1)
        if not ontology_1_file_extension == ontology_file_extension:
            continue
        compare_ontologies(
            ontology_1_location=ontology_path[0],
            ontology_2_location=ontology_path[1],
            results_folder_path=results_folder_path,
            verbose=verbose)
    
    
def get_ontology_files(right_folder: str, left_folder: str) -> tuple:
    left_files = set()
    right_files = set()
    left_file_paths = dict()
    right_file_paths = dict()
    for root, dirs, files in os.walk(right_folder):
        for file in files:
            left_files.add(file)
            left_file_paths[file] = os.path.join(root, file)
    for root, dirs, files in os.walk(left_folder):
        for file in files:
            right_files.add(file)
            right_file_paths[file] = os.path.join(root, file)
            
    both_files = left_files.intersection(right_files)
    only_left_files = left_files.difference(right_files)
    only_right_files = right_files.difference(left_files)
    
    both_file_paths = set()
    only_left_file_paths = set()
    only_right_file_paths = set()
    for file in both_files:
        both_file_paths.add(tuple([left_file_paths[file], right_file_paths[file]]))
    for file in only_left_files:
        only_left_file_paths.add(tuple([left_file_paths[file], str()]))
    for file in only_right_files:
        only_right_file_paths.add(tuple([str(), right_file_paths[file]]))
    
    return both_file_paths,only_left_file_paths,only_right_file_paths