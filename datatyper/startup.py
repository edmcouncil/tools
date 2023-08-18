import logging
import sys

from rdflib import Graph

from datatyper.datatypes_preparer import prepare_datatypes_dictionary, order_datatypes
from datatyper.postgress_datatype_creator import create_postgresql_datatypes
from datatyper.restriction_collector import collect_model_relevant_owl_restrictions
from util.merger import merge

logging.basicConfig(format='%(levelname)s %(asctime)s %(message)s', level=logging.INFO, datefmt='%m/%d/%Y %I:%M:%S %p')
# ontology = \
#     merge(
#         ontology_folder='/Users/pawel.garbacz/fibo/',
#         ontology_file_path='/Users/pawel.garbacz/fibo/AboutFIBOProd.rdf',
#         catalog_file_path='/Users/pawel.garbacz/fibo/catalog-v001.xml')
# ontology.serialize('fibo-prod.ttl')
ontology = Graph().parse('fibo-prod.ttl')
datatypes_attributes_map = collect_model_relevant_owl_restrictions(ontology=ontology)
datatypes_dictionary = prepare_datatypes_dictionary(datatypes_attributes_map=datatypes_attributes_map, ontology=ontology)
order_datatypes = order_datatypes(datatypes_dictionary=datatypes_dictionary, ordered_datatypes=dict(), attribute_rank=0)
postgresql_datatypes_sql = create_postgresql_datatypes(datatypes_dictionary=datatypes_dictionary, order_datatypes=order_datatypes)
with open('fibo.sql', 'w') as file:
    file.write(postgresql_datatypes_sql)
