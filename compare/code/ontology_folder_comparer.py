import logging
import os
import sys

from compare.code.common import *
from compare.code.comparison_config import ComparisonConfig
from compare.code.ontology_comparer import compare_ontology_revisions

FOLDER_NAME_LABEL = 'repository'


def compare_ontology_revisions_in_folders(
        comparison_identifier: str,
        left_revision_folder: str,
        right_revision_folder: str,
        left_revision_id: str,
        right_revision_id: str,
        config: ComparisonConfig) -> tuple:
    both_file_paths, only_left_file_paths, only_right_file_paths = \
        get_ontology_files(
            left_folder=left_revision_folder,
            right_folder=right_revision_folder,
            ontology_file_extension=config.default_ontology_file_extension)
    
    ontologies_diff_resources, ontologies_diff_axioms_for_same_subjects = \
        compare_common_ontology_revisions(
            both_file_paths=both_file_paths,
            default_ontology_file_extension=config.default_ontology_file_extension,
            left_revision_id=left_revision_id,
            right_revision_id=right_revision_id,
            config=config)
    
    diff_ontologies = \
        compare_repository_revisions(
            only_left_file_paths=only_left_file_paths,
            only_right_file_paths=only_right_file_paths,
            comparison_identifier=comparison_identifier,
            left_revision_id=left_revision_id,
            right_revision_id=right_revision_id,
            verbose=config.verbose)
    
    return diff_ontologies, ontologies_diff_resources, ontologies_diff_axioms_for_same_subjects


def compare_common_ontology_revisions(
        both_file_paths: set,
        default_ontology_file_extension: str,
        config: ComparisonConfig,
        left_revision_id: str,
        right_revision_id: str) -> tuple:
    ontologies_diff_resources = list()
    ontologies_diff_axioms_for_same_subjects = list()
    for ontology_path in both_file_paths:
        ontology_left_location = ontology_path[0]
        ontology_right_location = ontology_path[1]
        ontology_left_file_parent_folder, ontology_left_file_local_name = os.path.split(ontology_left_location)
        ontology_right_file_parent_folder, ontology_right_file_local_name = os.path.split(ontology_right_location)
        if not ontology_left_file_local_name == ontology_right_file_local_name:
            logging.error(
                msg='Something went wrong with comparison of revisions for' + ontology_left_file_local_name + ' and ' + ontology_right_file_local_name)
            sys.exit(-1)
        ontology_file_local_name = ontology_left_file_local_name
        ontology_file_name, ontology_file_extension = os.path.splitext(ontology_file_local_name)
        if not ontology_file_extension == default_ontology_file_extension:
            continue
        diff_resources_dict, diff_axioms_for_same_subjects_dict = \
            compare_ontology_revisions(
                ontology_revision_left_location=ontology_left_location,
                ontology_revision_right_location=ontology_right_location,
                ontology_name=ontology_file_name,
                left_revision_id=left_revision_id,
                right_revision_id=right_revision_id,
                config=config)
        if len(diff_resources_dict) > 0:
            ontologies_diff_resources.append(diff_resources_dict)
        if len(diff_axioms_for_same_subjects_dict) > 0:
            ontologies_diff_axioms_for_same_subjects.append(diff_axioms_for_same_subjects_dict)
    return ontologies_diff_resources, ontologies_diff_axioms_for_same_subjects


def compare_repository_revisions(
        only_left_file_paths: set,
        only_right_file_paths: set,
        comparison_identifier: str,
        verbose: bool,
        left_revision_id: str,
        right_revision_id: str) -> dict:
    diff_ontologies = dict()
    diff_ontologies[FOLDER_NAME_LABEL] = comparison_identifier
    left_but_not_right = \
        get_specific_constant(
            constant=ONTOLOGIES_LEFT_BUT_NOT_RIGHT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    right_but_not_left = \
        get_specific_constant(
            constant=ONTOLOGIES_RIGHT_BUT_NOT_LEFT,
            left_specific=left_revision_id,
            right_specific=right_revision_id)
    if verbose:
        diff_ontologies[left_but_not_right] = only_left_file_paths
        diff_ontologies[right_but_not_left] = only_right_file_paths
    else:
        diff_ontologies[left_but_not_right] = len(only_left_file_paths)
        diff_ontologies[right_but_not_left] = len(only_right_file_paths)

    return diff_ontologies


def get_ontology_files(left_folder: str, right_folder: str, ontology_file_extension: str) -> tuple:
    left_files = set()
    right_files = set()
    left_file_paths = dict()
    right_file_paths = dict()
    for root, dirs, files in os.walk(left_folder):
        for file in files:
            left_files.add(file)
            left_file_paths[file] = os.path.join(root, file)
    for root, dirs, files in os.walk(right_folder):
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
    
    return both_file_paths, only_left_file_paths, only_right_file_paths
