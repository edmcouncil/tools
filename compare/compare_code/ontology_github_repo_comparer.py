import logging
import os
import shutil

from git import Repo

from compare.compare_code.comparison_config import ComparisonConfig
from compare.compare_code.ontology_comparer_writer import save_deltas
from compare.compare_code.ontology_revisions_comparer import compare_ontology_revisions_in_folders
from compare.compare_code.utils import create_folder_if_not_exists

TEMP_FOLDER = 'temp/'
TEMP_LEFT_SUBFOLDER = 'temp/left'
TEMP_RIGHT_SUBFOLDER = 'temp/right'
RESULTS_FOLDER = 'results'


def compare_ontology_github_repo(
        repo_github_url: str,
        left_revision_id: str,
        right_revision_id: str,
        config: ComparisonConfig,
        outputs: str):
    logging.info(msg='Cloning ' + repo_github_url + ' to local file system.')
    
    repo_github_name = repo_github_url.split('/')[-1]
    
    outputs_temp = os.path.join(outputs, TEMP_FOLDER)
    outputs_temp_left = os.path.join(outputs, TEMP_LEFT_SUBFOLDER)
    outputs_temp_right = os.path.join(outputs, TEMP_RIGHT_SUBFOLDER)
    outputs_results = os.path.join(outputs, RESULTS_FOLDER)
    
    create_folder_if_not_exists(outputs_temp)
    create_folder_if_not_exists(outputs_temp_left)
    create_folder_if_not_exists(outputs_temp_right)
    create_folder_if_not_exists(outputs_results)
    
    logging.info(msg='Cloning revision ' + left_revision_id)
    git_repo_left = Repo.clone_from(url=repo_github_url, to_path=outputs_temp_left)
    git_repo_left.git.reset(left_revision_id, '--hard')
    
    logging.info(msg='Cloning revision ' + right_revision_id)
    git_repo_right = Repo.clone_from(url=repo_github_url, to_path=outputs_temp_right)
    git_repo_right.git.reset(right_revision_id, '--hard')
    
    logging.info(msg='Comparing revision ' + left_revision_id + ' to ' + right_revision_id)
    
    diff_ontologies, ontologies_diff_resources, ontologies_diff_axioms_for_same_subjects = \
        compare_ontology_revisions_in_folders(
            comparison_identifier=repo_github_name,
            left_revision_folder=outputs_temp_left,
            right_revision_folder=outputs_temp_right,
            left_revision_id=left_revision_id,
            right_revision_id=right_revision_id,
            config=config)
    
    logging.info(msg='Saving comparison results')
    
    save_deltas(
        comparison_identifier=repo_github_name,
        left_revision_id=left_revision_id,
        right_revision_id=right_revision_id,
        diff_ontologies_dict=diff_ontologies,
        diff_resource_dicts_list=ontologies_diff_resources,
        diff_axioms_for_same_subjects_dicts_list=ontologies_diff_axioms_for_same_subjects,
        config=config,
        output_folder=outputs_results)
    
    git_repo_left.close()
    git_repo_right.close()
    
    shutil.rmtree(outputs_temp)
