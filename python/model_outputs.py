import json
import os
import pandas as pd
import numpy as np
from objects import *
from simulation import *
from models import *

# Dictionary for reading data
scene_vals = {
    'name':[],
    'deterministic':[], 
    'stochastic':[],
    'sprt':[],
    'abstraction_sp':[],
    'abstraction_pp':[]
    }
# Directory where scene JSONs are
dir = "../data/json/pilot3/"
# Directory to write CSV to
w_dir = "../data/model/pilot3/"

json_files = [pos_json for pos_json in os.listdir(dir) if pos_json.endswith('.json')]

for file in json_files:
    with open(dir+file, 'r') as f:
        scene_args = json.loads(f.read())
        scene_vals['name'].append(scene_args['name'])
        scene_vals['deterministic'].append(determinstic_simulation(
            (scene_args)
        ))
        scene_vals['stochastic'].append(stochastic_simulation(
            (scene_args)
        ))
        scene_vals['sprt'].append(sprt(
            (scene_args)
        ))
        scene_vals['abstraction_sp'].append(abstraction_simulation_sp(
            (scene_args)
        ))
        scene_vals['abstraction_pp'].append(abstraction_simulation_pp(
            (scene_args)
        ))
        
with open(w_dir+'models.json', 'w') as f:
    json.dump(scene_vals, f)

    