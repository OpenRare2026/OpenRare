import os
import sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
DEV = os.path.join(ROOT, 'dev')
for p in (ROOT, DEV):
    if p not in sys.path:
        sys.path.insert(0, p)

import json
import pandas as pd
import rag_hpo as rh
import postprocess as pp

# Fake LLM client
class FakeLLM:
    def __init__(self):
        self.calls = []
    def query(self, user_input, system_message, max_retries=5):
        self.calls.append((user_input, system_message))
        # If payload looks like generate_hpo_terms (has candidates), return an hpo_id
        try:
            d = json.loads(user_input)
            if isinstance(d, dict) and 'phrase' in d and 'candidates' in d:
                # return a JSON object with hpo_id matching first candidate
                if d['candidates']:
                    return json.dumps({'hpo_id': d['candidates'][0]['id']})
                else:
                    return json.dumps({'hpo_id': None})
        except Exception:
            pass
        # Default simple response for system_message_I: return JSON phenotypes
        if 'phenotypes' in system_message or 'identify' in system_message:
            return json.dumps({'phenotypes': [{'phrase': 'fever', 'category': 'Abnormal', 'unique_metadata': [{'phrase': 'fever', 'hp_id': 'HP:0001945'}], 'original_sentence': 'Patient has fever', 'patient_id': 1}]})
        return '""'

rh.llm_client = FakeLLM()

print('Running generate_hpo_terms smoke test...')
row = pd.DataFrame([{
    'phrase': 'fever',
    'category': 'Abnormal',
    'original_sentence': 'Patient has fever',
    'unique_metadata': [{'phrase': 'fever', 'hp_id': 'HP:0001945'}]
}])
res = rh.generate_hpo_terms(row, rh.system_message_II)
print('generate_hpo_terms output:')
print(res.to_dict(orient='records'))

print('\nTesting postprocess.get_ols_term_status with invalid input (should skip):')
print(pp.get_ols_term_status('BAD_ID'))

print('\nAll unit smoke tests completed.')

