import json
import os

from rdflib import Graph

from constants import IS_COPULA, IS_A_COPULA, PREFIX_DECLARATION, COMMON_PREFIX_DECLARATIONS
from gpt.sw_regexes import owl_class_prefix_desc_regex, label_regex, def_regex, ex_regex, notes_regex, prefix_regex, \
    isDefinedBy_regex, isDefinedIn_regex


def __is_syntactically_correct(owl_description: str) -> bool:
    extended_owl_description = COMMON_PREFIX_DECLARATIONS + '\n' + PREFIX_DECLARATION + '\n' + owl_description
    temp_file = open(file='temp.ttl', mode='w')
    temp_file.write(extended_owl_description)
    temp_file.close()
    temp_file = open(file='temp.ttl', mode='r')
    graph = Graph()
    try:
        graph.parse(temp_file)
    except Exception as exception:
        temp_file.close()
        os.remove('temp.ttl')
        return False
    temp_file.close()
    os.remove('temp.ttl')
    return True


ontology_file = open(file=r'/Users/pawel.garbacz/Documents/edmc/python/projects/edmc_tools/resources/dev.fibo-quickstart.ttl',mode='r')
json_text = str()

ontology_doc = ontology_file.read()
count=0
owl_class_descriptions = owl_class_prefix_desc_regex.findall(string=ontology_doc)
for owl_class_description in owl_class_descriptions:
    owl_class_labels = label_regex.findall(string=owl_class_description)
    owl_class_definitions = def_regex.findall(string=owl_class_description)
    owl_class_examples = ex_regex.findall(string=owl_class_description)
    owl_class_notes = notes_regex.findall(string=owl_class_description)
    if len(owl_class_labels) > 0 and len(owl_class_definitions) > 0 and (len(owl_class_examples) > 0 or len(owl_class_notes)) > 0:
        owl_class_label = owl_class_labels[0].replace('"', str()).strip()
        owl_class_definition = owl_class_definitions[0].replace('"', str()).strip()
        
        if owl_class_definition.startswith('a ') or owl_class_definition.startswith('an ') or owl_class_definition.startswith('the '):
            copula = IS_COPULA
        else:
            copula = IS_A_COPULA
        human_readable_text = owl_class_label.capitalize() + copula + owl_class_definition + '.'
        human_readable_text += ' ' + ' '.join(owl_class_notes).strip()
        human_readable_text += ' ' + ' '.join(owl_class_examples).strip()
        human_readable_text = human_readable_text.replace('"', str()).strip()
        
        prefixes = prefix_regex.findall(string=owl_class_description)
        owl_class_description = isDefinedBy_regex.sub(repl=str(), string=owl_class_description)
        owl_class_description = isDefinedIn_regex.sub(repl=str(), string=owl_class_description)
        for prefix in prefixes:
            if '-' in prefix:
                owl_class_description = owl_class_description.replace(prefix, 'ontology:')

        if __is_syntactically_correct(owl_description=owl_class_description):
            prompt_text = human_readable_text + '\n###\n'
            completion_text = ' ' + owl_class_description + '\n|||\n'
            json_text += json.dumps({'prompt': prompt_text, 'completion': completion_text})
            json_text += '\n'
            count += 1
        else:
            print('Incorrect OWL document : ', PREFIX_DECLARATION + '\n' + owl_class_description[:50].strip())
print(count)
gpt_fine_tune_file = open(file='gpt_fine_tune_file.jsonl', mode='w', encoding='UTF-8')
gpt_fine_tune_file.write(json_text)
gpt_fine_tune_file.close()



        

