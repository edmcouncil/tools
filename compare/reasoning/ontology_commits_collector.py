import logging

from git import Repo

from compare.compare_code.utils import create_folder_if_not_exists


def collect_consolidated_ontology_commits(repo_github_url: str, temp_folder: str, outputs_folder: str):
    logging.info(msg='Cloning ' + repo_github_url + ' to local file system.')
    
    # create_folder_if_not_exists(temp_folder)
    # create_folder_if_not_exists(outputs_folder)
    # git_repo = Repo.clone_from(url=repo_github_url, to_path=temp_folder)
    git_repo = Repo.init(path=temp_folder)
    for commit in git_repo.iter_commits(rev='master'):
        commit_id = commit.hexsha
        commit_time = commit.committed_datetime
        print(commit_time)
        git_repo.head.reset(commit=commit_id)
        v=0
    
    