import json
import numpy as np
import pandas as pd
import os
from collections import defaultdict

with open("config.json", "r") as read_file:
    config = json.load(read_file)

ans_folder = config['ans_folder']

collected_answers = defaultdict(list)

for dirpath, dirnames, filenames in os.walk(ans_folder):
    for filename in [f for f in filenames if f.endswith(".txt")]:
        
        directory = dirpath.split('/')
        domain, task_type = directory[-2], directory[-1]
        task_file = open(os.path.join(dirpath, filename), "r")
        task_text = task_file.read().split('===')
        
        if len(task_text) < 2:
            continue
        
        collected_answers['pro-trope'].append(task_text[0])
        collected_answers['anti-trope'].append(task_text[1])
        collected_answers['domain'].append(domain)
        collected_answers['task_type'].append(task_type)
        collected_answers['is_clear'].append(-1)
        collected_answers['is_similar'].append(-1)
        
data_raw = pd.DataFrame.from_dict(collected_answers)
data_raw.to_csv("response_table_raw.tsv", sep="\t")
