import argparse
import logging
import os
import sys



from compare.comparision_config import ComparisionConfig
from compare.ontology_github_repo_comparer import compare_ontology_github_repos


if __name__ == "__main__":
    
    parser = argparse.ArgumentParser(
        description='Compares two revisions of an ontology versioned-controlled in a GitHub repository')
    parser.add_argument('--github', help='IRI for GitHub repository')
    parser.add_argument('--left', help='Left revision commit id')
    parser.add_argument('--right', help='Right revision commit id')
    parser.add_argument('--outputs', default='outputs', help='Path to output folder')
    parser.add_argument('--verbose', default=True, action=argparse.BooleanOptionalAction)
    parser.add_argument('--log_file', default=str())
    args = parser.parse_args()
    
    if len(args.log_file) > 0:
        logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO,datefmt='%m/%d/%Y %I:%M:%S %p', filename=args.log_file)
    else:
        logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO,datefmt='%m/%d/%Y %I:%M:%S %p')
    
    compare_ontology_github_repos(
        repo_github_url=args.github,
        left_revision_id=args.left,
        right_revision_id=args.right,
        config=ComparisionConfig(verbose=args.verbose),
        outputs=args.outputs)
