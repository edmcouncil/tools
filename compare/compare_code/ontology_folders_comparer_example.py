import logging
import time

from compare.compare_code.comparison_config import ComparisonConfig
from compare.compare_code.ontology_folders_comparer import compare_ontology_folders

timestr = time.strftime("%Y%m%d-%H%M%S")
logging_file_name = ''

if len(logging_file_name) > 0:
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p', filename=logging_file_name)
else:
    logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')

compare_ontology_folders(
    comparison_identifier='ontology',
    left_revision_folder='/compare_test/ontology_1',
    right_revision_folder='/compare_test/ontology_2',
    left_revision_id='1',
    right_revision_id='2',
    config=ComparisonConfig(verbose=True),
    outputs='out')
