import json
import os
import re

from rdflib import Graph

from constants import IS, IS_A, PREFIX_DECLARATION, COMMON_PREFIX_DECLARATIONS


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


owl_class_desc_regex = re.compile(pattern=r'[a-z\-]+:\w+\s*a\s+owl:Class.+?\.\n', flags=re.DOTALL)
label_regex = re.compile(pattern=r'rdfs:label\s+"(.+?)"')
def_regex = re.compile(pattern=r'skos:definition\s+"(.+?)"')
ex_regex = re.compile(pattern=r'skos:example\s+(.+?)"', flags=re.DOTALL)
notes_regex = re.compile(pattern=r'fibo-fnd-utl-av:explanatoryNote.+?"(.+?)"', flags=re.DOTALL)
prefix_regex = re.compile(pattern=r'[a-z\-]+:')
isDefinedBy_regex = re.compile(pattern=r'rdfs:isDefinedBy\s+[a-z\-]+:\s+;', flags=re.DOTALL)
isDefinedIn_regex = re.compile(pattern=r'fibo-fnd-rel-rel:isDefinedIn\s+.+?;', flags=re.DOTALL)

ontology_file = open(file=r'/Users/pawel.garbacz/Documents/edmc/python/projects/edmc_tools/resources/dev.fibo-quickstart.ttl',mode='r')
json_text = str()

ontology_doc = ontology_file.read()
count=0
owl_class_descriptions = owl_class_desc_regex.findall(string=ontology_doc)
for owl_class_description in owl_class_descriptions:
    owl_class_labels = label_regex.findall(string=owl_class_description)
    owl_class_definitions = def_regex.findall(string=owl_class_description)
    owl_class_examples = ex_regex.findall(string=owl_class_description)
    owl_class_notes = notes_regex.findall(string=owl_class_description)
    if len(owl_class_labels) > 0 and len(owl_class_definitions) > 0 and (len(owl_class_examples) > 0 or len(owl_class_notes)) > 0:
        owl_class_label = owl_class_labels[0].replace('"', str()).strip()
        owl_class_definition = owl_class_definitions[0].replace('"', str()).strip()
        
        if owl_class_definition.startswith('a ') or owl_class_definition.startswith('an ') or owl_class_definition.startswith('the '):
            copula = IS
        else:
            copula = IS_A
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



        

