import glob
import os
import re
import uuid

import xml.etree.ElementTree as ET

CATALOG_FILE_NAME = 'catalog-v001.xml'

URI_PATTERN = re.compile(pattern='uri="\.(.+)"')


def fix_catalog_file_ids(path: str):
    catalog_files = glob.glob(path + '/**/catalog-v001.xml', recursive=True)
    for catalog_file in catalog_files:
        catalog = ET.parse(source=catalog_file)
        for ontology_ref in catalog.getroot():
            ontology_ref.attrib['id'] = str(uuid.uuid4())
        catalog.write(catalog_file)

    
fix_catalog_file_ids('/Users/pawel.garbacz/idmp')
