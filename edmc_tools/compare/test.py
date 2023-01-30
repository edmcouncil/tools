import logging
import time

from compare.comparision_config import ComparisionConfig
from compare.ontology_github_repo_comparer import compare_ontology_github_repos

timestr = time.strftime("%Y%m%d-%H%M%S")
logging_file_name = ''

if len(logging_file_name) > 0:
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO,
                        datefmt='%m/%d/%Y %I:%M:%S %p', filename=logging_file_name)
else:
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO,
                        datefmt='%m/%d/%Y %I:%M:%S %p')

compare_ontology_github_repos(
    repo_github_url='https://github.com/iofoundry/ontology.git',
    left_revision_commit='aa937f32d6c8eb0e61e7cf513d58d514ecb61bbb',
    right_revision_commit='b274424dd70d8d9fc843795d53bf699c6565dc87',
    config=ComparisionConfig(verbose=True))
