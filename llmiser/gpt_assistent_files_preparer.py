import os
import re

import pandas


def prepare_gpt_files_from_data_dictionary(data_dictionary_file_path: str, gpt_files_folder_path: str):
    gpt_texts = dict()
    with open(file=data_dictionary_file_path, mode='r') as data_dictionary_file:
        data_dictionary_text = data_dictionary_file.read()
        data_dictionary_text = re.sub(pattern='@\w+', string=data_dictionary_text, repl='')
    with open(file=data_dictionary_file_path, mode='w') as data_dictionary_file:
        data_dictionary_file.write(data_dictionary_text)
    data_dictionary = pandas.read_csv(data_dictionary_file_path)
    classes_dictionary = data_dictionary[data_dictionary['Type'] == 'Class']
    for index, class_row in classes_dictionary.iterrows():
        gpt_concept_description = str()
        if isinstance(class_row['Term'], str):
            ontology_name = class_row['Ontology']
            term = class_row['Term'][0].upper() + class_row['Term'][1:]
            term = term.strip()
            if isinstance(class_row['Definition'], str):
                definition = class_row['Definition'].strip()
                definition = definition[0].lower() + definition[1:]
                gpt_concept_description = term + ' is defined as ' + definition + '.'
            if isinstance(class_row['Synonyms'], str):
                gpt_concept_description += ' ' + term + ' has synonyms ' + class_row['Synonyms'].strip() + '.'
            if isinstance(class_row['Examples'], str):
                gpt_concept_description += ' ' + term + ' has examples ' + class_row['Examples'].strip() + '.'
            if isinstance(class_row['Explanations'], str):
                gpt_concept_description += ' ' + class_row['Explanations'].strip()
            if isinstance(class_row['GeneratedDefinition'], str):
                gpt_concept_description += ' ' + class_row['GeneratedDefinition'].strip()
            if len(gpt_concept_description) > 0:
                if ontology_name in gpt_texts:
                    gpt_text = gpt_texts[ontology_name]
                else:
                    gpt_text = str()
                gpt_text += '\n' + gpt_concept_description
                gpt_texts[ontology_name] = gpt_text
     
    for ontology_name, gpt_text in gpt_texts.items():
        gpt_file = ontology_name.replace(' ', '_') + '.txt'
        gpt_file_path = os.path.join(gpt_files_folder_path, gpt_file)
        with open(file=gpt_file_path, mode='w') as gpt_file:
            gpt_file.write(gpt_text)
   
    
prepare_gpt_files_from_data_dictionary(data_dictionary_file_path='datadictionary.csv', gpt_files_folder_path='gpt_files')
    