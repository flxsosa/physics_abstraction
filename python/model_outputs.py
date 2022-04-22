import json
import os
from objects import *
from simulation import *
from models import *

def main():
    # Dictionary for reading data
    scene_vals = {
        'name':[],
        'deterministic':[], 
        'abstraction':[]
        }
    # Directory where scene JSONs are
    dir = "../data/json/pilot3/"
    # Directory to write CSV to
    w_dir = "../data/model/pilot3/"
    # Gather scene jsons
    json_files = [pos_json for pos_json in os.listdir(dir) if pos_json.endswith('.json')]

    # Collect model predictions per scene
    for file in json_files:
        with open(dir+file, 'r') as f:
            scene_args = json.loads(f.read())
            scene_vals['name'].append(scene_args['name'])
            scene_vals['deterministic'].append(determinstic_simulation(
                (scene_args)
            ))
            scene_vals['abstraction'].append(abstraction_simulation_pp(
                (scene_args),N=35,D=200,E=0.09
            ))

    # Save modle predictions to file    
    with open(w_dir+'models.json', 'w') as f:
        print(f"Writing models.json to {w_dir}")
        json.dump(scene_vals, f)

if __name__ == "__main__":
    main() 