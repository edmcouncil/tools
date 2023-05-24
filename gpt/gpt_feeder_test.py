import time

from rdflib import Graph, OWL

from gpt.gpt_feeder import get_finetune_json_from_sw_types

fibo_location = '../resources/fibo/AboutFIBODevMerged.ttl'
fibo_file = open(file=fibo_location,mode='r')
fibo_text = fibo_file.read()
fibo = Graph()
fibo.parse(fibo_location)
fibo_finetune_json = get_finetune_json_from_sw_types(ontology=fibo, sw_types=[OWL.Class], ontology_file_text=fibo_text)
timestr = time.strftime("%Y%m%d-%H%M%S")
gpt_fine_tune_file = open(file='gpt_finetune_fibo_' + timestr + '.jsonl', mode='w', encoding='UTF-8')
gpt_fine_tune_file.write(fibo_finetune_json)
gpt_fine_tune_file.close()