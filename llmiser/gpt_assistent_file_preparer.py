import re

from rdflib import Graph
import pandas
import numpy


def prepare_gpt_file_from_data_dictionary(data_dictionary_file_path: str, gpt_file_path: str):
    with open(file=data_dictionary_file_path, mode='r') as data_dictionary_file:
        data_dictionary_text = data_dictionary_file.read()
        data_dictionary_text = re.sub(pattern='@\w+', string=data_dictionary_text, repl='')
    with open(file=data_dictionary_file_path, mode='w') as data_dictionary_file:
        data_dictionary_file.write(data_dictionary_text)
    data_dictionary = pandas.read_csv(data_dictionary_file_path)
    concepts_dictionary = data_dictionary[(data_dictionary['Type'] == 'Class') | (data_dictionary['Type'] == 'Individual')]
    gpt_concept_descriptions = set()
    for index, concept_row in concepts_dictionary.iterrows():
        gpt_concept_description = str()
        if isinstance(concept_row['Term'], str):
            term = concept_row['Term'][0].upper() + concept_row['Term'][1:]
            term = term.strip()
            if isinstance(concept_row['Definition'], str):
                definition = concept_row['Definition'].strip()
                definition = definition[0].lower() + definition[1:]
                gpt_concept_description = term + ' is defined as ' + definition + '.'
            if isinstance(concept_row['Synonyms'], str):
                gpt_concept_description += ' ' + term + ' has synonyms ' + concept_row['Synonyms'].strip() + '.'
            if isinstance(concept_row['Examples'], str):
                gpt_concept_description += ' ' + term + ' has examples ' + concept_row['Examples'].strip() + '.'
            if isinstance(concept_row['Explanations'], str):
                gpt_concept_description += ' ' + concept_row['Explanations'].strip()
            if isinstance(concept_row['GeneratedDefinition'], str):
                gpt_concept_description += ' ' + concept_row['GeneratedDefinition'].strip()
            if len(gpt_concept_description) > 0:
                gpt_concept_descriptions.add(gpt_concept_description)
    gpt_text = '\n'.join(gpt_concept_descriptions)
    
    with open(file=gpt_file_path, mode='w') as gpt_file:
        gpt_file.write(gpt_text)
   
    
prepare_gpt_file_from_data_dictionary(data_dictionary_file_path='datadictionary.csv', gpt_file_path='fibo_gpt.txt')
    