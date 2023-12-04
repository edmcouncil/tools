import datetime
import logging

from compare.reasoning.ontology_commits_collector import collect_consolidated_ontology_commits
from compare.reasoning.reasoner_executor import run_reasoner_over_folder

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.WARN, datefmt='%m/%d/%Y %I:%M:%S %p')
collect_consolidated_ontology_commits(
    repo_github_url='https://github.com/edmcouncil/idmp',
    repo_folder='./idmp_repo/',
    consolidated_ontologies_folder='./idmp_ontology_versions/',
    nearest_commit_ignore_span=1,
    merge_ontology_file='AboutIDMPDev-ReferenceIndividuals.rdf',
    first_commit_date=datetime.date(year=2023, month=7, day=1))
run_reasoner_over_folder(folder_path='./idmp_ontology_versions/')