import logging
import os
import shutil

from git import Repo

from compare.code.comparison_config import ComparisonConfig
from compare.code.ontology_comparer_writer import save_deltas
from compare.code.ontology_folder_comparer import compare_ontology_revisions_in_folders
from compare.code.utils import create_folder_if_not_exists

TEMP_FOLDER = 'temp/'
TEMP_LEFT_SUBFOLDER = 'temp/left'
TEMP_RIGHT_SUBFOLDER = 'temp/right'
RESULTS_FOLDER = 'results'


def compare_ontology_folders(
        left_revision_folder: str,
        right_revision_folder: str,
        config: ComparisonConfig,
        left_revision_id: str,
        right_revision_id: str,
        comparison_identifier: str,
        outputs: str):
    logging.info(msg='Comparing revision ' + left_revision_folder + ' to ' + right_revision_folder)
    
    diff_ontologies, ontologies_diff_resources, ontologies_diff_axioms_for_same_subjects = \
        compare_ontology_revisions_in_folders(
            comparison_identifier=comparison_identifier,
            left_revision_folder=left_revision_folder,
            right_revision_folder=right_revision_folder,
            left_revision_id=left_revision_id,
            right_revision_id=right_revision_id,
            config=config)
    
    logging.info(msg='Saving comparison results')
    
    save_deltas(
        comparison_identifier=comparison_identifier,
        left_revision_id=left_revision_id,
        right_revision_id=right_revision_id,
        diff_ontologies_dict=diff_ontologies,
        diff_resource_dicts_list=ontologies_diff_resources,
        diff_axioms_for_same_subjects_dicts_list=ontologies_diff_axioms_for_same_subjects,
        config=config,
        output_folder=outputs)
    
