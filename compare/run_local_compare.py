import argparse
import logging

from compare.compare_code.comparison_config import ComparisonConfig
from compare.compare_code.ontology_folders_comparer import compare_ontology_folders
from compare.compare_code.ontology_github_repo_comparer import compare_ontology_github_repos


def run():
    parser = argparse.ArgumentParser(description='Compares folders with ontology files.')
    parser.add_argument('--left', help='Path to the left folder.')
    parser.add_argument('--right', help='Path to the right folder.')
    parser.add_argument('--comparison_identifier', default='ontology')
    parser.add_argument('--outputs', default='outputs', help='Path to output folder')
    parser.add_argument('--verbose', default=True)
    parser.add_argument('--log_file', default=str())
    args = parser.parse_args()
    
    if len(args.log_file) > 0:
        logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO,datefmt='%m/%d/%Y %I:%M:%S %p', filename=args.log_file)
    else:
        logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO,datefmt='%m/%d/%Y %I:%M:%S %p')
    
    compare_ontology_folders(
        comparison_identifier=args.comparison_identifier,
        left_revision_folder=args.left,
        right_revision_folder=args.right,
        left_revision_id=args.left,
        right_revision_id=args.right,
        config=ComparisonConfig(verbose=args.verbose),
        outputs=args.outputs)
