import logging
import time

from compare.compare_code.comparison_config import ComparisonConfig
from compare.compare_code.ontology_github_repo_comparer import compare_ontology_github_repo

timestr = time.strftime("%Y%m%d-%H%M%S")
logging_file_name = ''

if len(logging_file_name) > 0:
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p', filename=logging_file_name)
else:
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')

compare_ontology_github_repo(
    repo_github_url='https://github.com/edmcouncil/fibo',
    left_revision_id='master_2022Q4',
    right_revision_id='master_2023Q1',
    config=ComparisonConfig(verbose=True),
    outputs='out')
