import json
import logging
import os
import shutil

from git import Repo

from compare.compare_code.utils import create_folder_if_not_exists
from util.merger import merge


def collect_consolidated_ontology_commits(
        repo_github_url: str,
        repo_folder: str,
        consolidated_ontologies_folder: str,
        nearest_commit_ignore_span):
    logging.info(msg='Cloning ' + repo_github_url + ' to local file system.')
    
    create_folder_if_not_exists(repo_folder)
    create_folder_if_not_exists(consolidated_ontologies_folder)
    git_repo = Repo.clone_from(url=repo_github_url, to_path=repo_folder)
    commit_count = -1
    consolidated_ontologies_register = dict()
    for commit in git_repo.iter_commits(rev='master'):
        commit_count += 1
        if commit_count % nearest_commit_ignore_span == 0:
            commit_id = commit.hexsha
            commit_time = commit.committed_datetime
            consolidated_ontologies_register[commit_id] = str(commit_time)
            git_repo.git.checkout(commit_id)
            ontology_path = os.path.join(repo_folder, 'AboutIDMPDev-ReferenceIndividuals.rdf')
            if os.path.isfile(ontology_path):
                catalog_file_path = os.path.join(repo_folder, 'catalog-v001.xml')
                try:
                    merged_ontology_at_commit = merge(ontology_folder=repo_folder, ontology_file_path=ontology_path, catalog_file_path=catalog_file_path)
                    merged_ontology_path = os.path.join(consolidated_ontologies_folder,  commit_id + '.ttl')
                    merged_ontology_at_commit.serialize(merged_ontology_path)
                except Exception as error:
                    print(commit_id, error)
    with open(os.path.join(consolidated_ontologies_folder, 'ontologies_register.json'), 'w') as file:
        json.dump(consolidated_ontologies_register, file)
    git_repo.close()
    shutil.rmtree(repo_folder)