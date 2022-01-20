import json
import os
import pandas as pd
import numpy as np
from objects import *
from simulation import *
from models import *

# Object map
obj_map = {
    "Ball":Ball,
    "Container":Container,
    "Goal":Goal     
}

# Dictionary for reading data
scene_vals = {'name':[],'ticks':[], 'tick_mean':[]}
# Directory where scene JSONs are
dir = "../data/json/pilot3/"
# Directory to write CSV to
w_dir = "../data/model/pilot3/"

json_files = [pos_json for pos_json in os.listdir(dir) if pos_json.endswith('.json')]

for file in json_files:
    with open(dir+file, 'r') as f:
        scene_args = json.loads(f.read())
        scene_vals['name'].append(scene_args['name'])
        try:
            scene_vals['ticks'].append(scene_args['tick_samples'])
            scene_vals['tick_mean'].append(np.mean(scene_args['tick_samples']))
        except KeyError:
            scene_vals['ticks'].append([scene_args['tick']])
            scene_vals['tick_mean'].append(scene_args['tick'])

with open(w_dir+'simulation_vals.json', 'w') as f:
    json.dump(scene_vals, f)

    