import glob
import os
import re

CATALOG_FILE_NAME = 'catalog-v001.xml'

URI_PATTERN = re.compile(pattern='uri="\.(.+)"')


def check_catalog_file(ontology_location: str):
    catalog_file = open(os.path.join(ontology_location, CATALOG_FILE_NAME), 'r')
    catalog_file_content = catalog_file.read()
    uris = URI_PATTERN.findall(string=catalog_file_content)
    for uri in uris:
        file_location = ontology_location+uri
        if not os.path.isfile(file_location):
            print("MISREFERENCED", uri)

    files = glob.glob(ontology_location+'/**/*.rdf', recursive=True)
    files = set(files)
    for file in files:
        relative_file = file.replace(ontology_location, '')
        if not relative_file in uris:
            print('UNREFERENCED', relative_file)
    
    
check_catalog_file('/Users/pawel.garbacz/idmp')
