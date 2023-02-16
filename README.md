# EDMC Tools

:warning: **Work in progress**

This ia a repository that stores some utils needed for the ontology development.
All tools assumed that if you want to use them, you need to have Python 3.* installed (3.9 is recommended.)

## Ontology revision comparison
Currently, the tool runs three comparisons:
- with respect to the deleted and created **ontologies** (i.e., ontology files) in the repository's revisions
  - only the .rdf extension files are processed
- with respect to the deleted and created **resources** in ontologies in both revisions
- with respect to the changes in **axioms**, where the resources from both revisions are subjects.

The tool can be run in two modes:
- no-verbose where only the counts of differences are given
- verbose.

[run_compare](https://github.com/edmcouncil/tools/blob/main/edmc_tools/run_compare.py) is a Python script that compares two snapshots of a single ontology GitHub repository.
### How to run
Example:
In your command line/terminal run python `run_compare.py` with parameters - see below.
```
python run_compare.py --github https://github.com/iofoundry/ontology --left b7fe31cb7cc43c3ae75fbcfec3cb009872be587f --right Release_202301 --verbose False --outputs Home/ontology/compare/ 
```
### Parameters
```
--github URL of a public GitHub repository
--left commit or tag of one repository snapshot to compare
--right commit or tag of another repository snapshot to compare
--verbose if outputs will be verbose (default); otherwise --no-verbose
--outputs path to output folder (default = 'outputs')
```
### Results
After a successful comparison, the results will be saved to th `results` folder.
All results are provided in two formats: json and xlsx except for verbose comparison of axioms.

