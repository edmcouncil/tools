import json

import pandas

from gpt.gpt_constants import PROMPT_SUFFIX, COMPLETION_SUFFIX

fine_tune_inferences = str()

training_inferences = pandas.read_json(path_or_buf='folio-train.json', lines=True)
training_inferences = training_inferences[['conclusion', 'premises', 'label']]
valid_training_inferences = training_inferences[training_inferences['label'] == 'True']
for valid_training_inference in valid_training_inferences.iterrows():
    premises = valid_training_inference[1]['premises']
    premises = [premise.strip() for premise in premises]
    conclusion = valid_training_inference[1]['conclusion'].strip()
    prompt_text = 'Because:\n' + '\n'.join(premises) + '\n' + 'Therefore:' + PROMPT_SUFFIX
    completion_text = ' ' + conclusion + COMPLETION_SUFFIX
    fine_tune_inferences += json.dumps({'prompt': prompt_text, 'completion': completion_text})
    fine_tune_inferences += '\n'

gpt_fine_tune_file = open(file='gpt_fine_tune_inferences.jsonl', mode='w', encoding='UTF-8')
gpt_fine_tune_file.write(fine_tune_inferences)
gpt_fine_tune_file.close()



        

