import argparse
import logging

from compare.compare_code.comparison_config import ComparisonConfig
from compare.compare_code.ontology_github_repo_comparer import compare_ontology_github_repo


def run():
    parser = argparse.ArgumentParser(description='Compares two revisions of an ontology versioned-controlled in a GitHub repository')
    parser.add_argument('--github', help='IRI for GitHub repository')
    parser.add_argument('--left', help='Left revision commit id')
    parser.add_argument('--right', help='Right revision commit id')
    parser.add_argument('--outputs', default='outputs', help='Path to output folder')
    parser.add_argument('--verbose', default=True)
    parser.add_argument('--log_file', default=str())
    args = parser.parse_args()
    
    if len(args.log_file) > 0:
        logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p', filename=args.log_file)
    else:
        logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')
    
    compare_ontology_github_repo(
        repo_github_url=args.github,
        left_revision_id=args.left,
        right_revision_id=args.right,
        config=ComparisonConfig(verbose=args.verbose),
        outputs=args.outputs)
