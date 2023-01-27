import os
import sys

from compare.common import LEFT_BUT_NOT_RIGHT, RIGHT_BUT_NOT_LEFT, LEFT_BUT_NOT_RIGHT_COUNT, RIGHT_BUT_NOT_LEFT_COUNT
from compare.ontology_comparer import compare_ontology_revisions

FOLDER_NAME_LABEL = 'repository'


def compare_ontology_revisions_in_folders(
        folder_name: str,
        left_revision_folder: str,
        right_revision_folder: str,
        default_ontology_file_extension='.rdf',
        verbose=False) -> tuple:
    both_file_paths, only_left_file_paths, only_right_file_paths = \
        get_ontology_files(
            left_folder=left_revision_folder,
            right_folder=right_revision_folder,
            ontology_file_extension=default_ontology_file_extension)

    ontologies_diff_resources, ontologies_diff_axioms_for_same_subjects = \
        compare_common_ontology_revisions(
            both_file_paths=both_file_paths,
            default_ontology_file_extension=default_ontology_file_extension,
            verbose=verbose)
    
    diff_ontologies = \
        compare_diff_ontology_revisions(
            only_left_file_paths=only_left_file_paths,
            only_right_file_paths=only_right_file_paths,
            folder_name=folder_name,
            verbose=verbose)

    return diff_ontologies, ontologies_diff_resources, ontologies_diff_axioms_for_same_subjects


def compare_common_ontology_revisions(both_file_paths: set, default_ontology_file_extension: str, verbose: bool) -> tuple:
    ontologies_diff_resources = list()
    ontologies_diff_axioms_for_same_subjects = list()
    for ontology_path in both_file_paths:
        ontology_left_location = ontology_path[0]
        ontology_right_location = ontology_path[1]
        ontology_left_file_parent_folder, ontology_left_file_local_name = os.path.split(ontology_left_location)
        ontology_right_file_parent_folder, ontology_right_file_local_name = os.path.split(ontology_right_location)
        # if not ontology_left_file_parent_folder == ontology_right_file_parent_folder:
        #     sys.exit(-1)
        if not ontology_left_file_local_name == ontology_right_file_local_name:
            sys.exit(-1)
        ontology_file_local_name = ontology_left_file_local_name
        ontology_file_name, ontology_file_extension = os.path.splitext(ontology_file_local_name)
        if not ontology_file_extension == default_ontology_file_extension:
            continue
        diff_resources_dict, diff_axioms_for_same_subjects_dict = \
            compare_ontology_revisions(
                ontology_revision_left_location=ontology_left_location,
                ontology_revision_right_location=ontology_right_location,
                verbose=verbose,
                ontology_name = ontology_file_name)
        ontologies_diff_resources.append(diff_resources_dict)
        ontologies_diff_axioms_for_same_subjects.append(diff_axioms_for_same_subjects_dict)
    return ontologies_diff_resources, ontologies_diff_axioms_for_same_subjects
    

def compare_diff_ontology_revisions(only_left_file_paths: set, only_right_file_paths: set, folder_name: str, verbose: bool) -> dict:
    diff_ontologies = dict()
    diff_ontologies[FOLDER_NAME_LABEL]=folder_name
    if verbose:
        diff_ontologies[LEFT_BUT_NOT_RIGHT_COUNT]=len(only_left_file_paths)
        diff_ontologies[RIGHT_BUT_NOT_LEFT_COUNT] = len(only_right_file_paths)
    else:
        diff_ontologies[LEFT_BUT_NOT_RIGHT] = only_left_file_paths
        diff_ontologies[RIGHT_BUT_NOT_LEFT] = only_right_file_paths
    return diff_ontologies
    
def get_ontology_files(right_folder: str, left_folder: str, ontology_file_extension: str) -> tuple:
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
    
    both_file_paths = list()
    only_left_file_paths = list()
    only_right_file_paths = list()
    for file in both_files:
        file_name, file_extension = os.path.splitext(file)
        if ontology_file_extension == file_extension:
            both_file_paths.append(tuple([left_file_paths[file], right_file_paths[file]]))
    for file in only_left_files:
        file_name, file_extension = os.path.splitext(file)
        if ontology_file_extension == file_extension:
            only_left_file_paths.append(file_name)
    for file in only_right_files:
        file_name, file_extension = os.path.splitext(file)
        if ontology_file_extension == file_extension:
            only_right_file_paths.append(file_name)
    
    return both_file_paths,only_left_file_paths,only_right_file_paths