# Ontology revision comparison
Currently, the tool runs three comparisons:
- with respect to the deleted and created **ontologies** (i.e., ontology files) in the repository's revisions
  - only the .rdf extension files are processed
- with respect to the deleted and created **resources** in ontologies in both revisions
- with respect to the changes in **axioms**, where the resources from both revisions are subjects.

The tool can be run in two modes:
- no-verbose where only the counts of differences are given
- verbose where the differences are explicitly shown.

We provide two scripts for ontology comparison - see below.
Before you run them you may want to install all scripts in this repository using pip:

`pip install .`

## GitHub repository compare tool
[github_compare](https://github.com/edmcouncil/tools/blob/main/edmc_tools/run_github_compare.py) is a Python script that compares two snapshots of a single ontology GitHub repository.
### How to run

Example:
In your command line/terminal run `github_compare` with parameters - see below.
```
github_compare --github https://github.com/iofoundry/ontology --left b7fe31cb7cc43c3ae75fbcfec3cb009872be587f --right Release_202301 --verbose False --outputs Home/ontology/compare/ 
```
### Parameters
```
--github URL of a public GitHub repository
--left commit or tag of one repository snapshot to compare
--right commit or tag of another repository snapshot to compare
--verbose if outputs will be verbose (default); otherwise --no-verbose
--outputs path to output folder (default = 'outputs')
--log_file path to log file (optional)
```


## Local folders compare tool
[local_compare](https://github.com/edmcouncil/tools/blob/main/edmc_tools/run_local_compare.py) is a Python script that compares two local folders with ontology files.

Example:
In your command line/terminal run python `local_compare.py` with parameters - see below.
```
local_compare --comparision_identifier fibo --left /ontologies/fibo/Q1 --right /ontologies/fibo/Q2 --verbose False --outputs Home/ontology/compare/ 
```
### Parameters
```
--left path to one ontology folder to compare
--right path to another ontology folder to compare
--verbose if outputs will be verbose (default); otherwise --no-verbose
--outputs path to output folder (default = 'outputs')
--comparison_identifier identifier for comparison, most likely the ontology name (default='ontology')
--log_file path to log file (optional)
```

### Results
After a successful comparison, the results for **both scripts** will be saved to th `results` folder.
All results are provided in two formats: json and xlsx except for verbose comparison of axioms.

