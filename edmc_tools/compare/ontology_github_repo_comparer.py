import logging
import shutil

from git import Repo

from compare.comparision_config import ComparisionConfig
from compare.ontology_comparer_writer import save_diff_dicts
from compare.ontology_folder_comparer import compare_ontology_revisions_in_folders
from compare.utils import create_folder_if_not_exists

TEMP_FOLDER = 'temp/'
TEMP_LEFT_SUBFOLDER = 'temp/left'
TEMP_RIGHT_SUBFOLDER = 'temp/right'
RESULTS_FOLDER = 'results'


def compare_ontology_github_repos(
        repo_github_url: str,
        left_revision_commit: str,
        right_revision_commit: str,
        config: ComparisionConfig):
    logging.info(msg='Cloning ' + repo_github_url + ' to local file system.')
    
    repo_github_name = repo_github_url.split('/')[-1]
    
    create_folder_if_not_exists(TEMP_FOLDER)
    create_folder_if_not_exists(TEMP_LEFT_SUBFOLDER)
    create_folder_if_not_exists(TEMP_RIGHT_SUBFOLDER)
    create_folder_if_not_exists(RESULTS_FOLDER)
    
    logging.info(msg='Cloning revision ' + left_revision_commit)
    git_repo_left = Repo.clone_from(url=repo_github_url, to_path=TEMP_LEFT_SUBFOLDER)
    git_repo_left.git.reset(left_revision_commit, '--hard')
    
    logging.info(msg='Cloning revision ' + right_revision_commit)
    git_repo_right = Repo.clone_from(url=repo_github_url, to_path=TEMP_RIGHT_SUBFOLDER)
    git_repo_right.git.reset(right_revision_commit, '--hard')
    
    logging.info(msg='Comparing revision ' + left_revision_commit + ' to ' + right_revision_commit)
    
    diff_ontologies, ontologies_diff_resources, ontologies_diff_axioms_for_same_subjects = \
        compare_ontology_revisions_in_folders(
            folder_name=repo_github_name,
            left_revision_folder=TEMP_LEFT_SUBFOLDER,
            right_revision_folder=TEMP_RIGHT_SUBFOLDER,
            config=config)
    
    logging.info(msg='Saving comparison results')
    
    save_diff_dicts(
        comparison_prefix=repo_github_name,
        diff_ontologies_list=[diff_ontologies],
        diff_resource_dicts_list=ontologies_diff_resources,
        diff_axioms_for_same_subjects_dicts_list=ontologies_diff_axioms_for_same_subjects,
        output_folder=RESULTS_FOLDER)
    
    git_repo_left.close()
    git_repo_right.close()
    
    shutil.rmtree(TEMP_FOLDER)
