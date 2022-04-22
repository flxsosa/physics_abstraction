from objects import *
from simulation import Scene, Physics, Graphics
import pandas as pd
import numpy as np
import os
import json
from models import load_object_arg_pairs

def sim(scene_args,N=5,D=100,E=0.9):
    '''
    Deterministic physics simulator. Model outputs are end
    state of the scene and the number of ticks of one run 
    of a scene with no noise.
    '''
    ticks = []
    collision_prob = 0
    # Run scene
    objects = []
    objs,args = load_object_arg_pairs(scene_args)
    for o,a in zip(objs, args):
        try:
            objects.append(o(*a))
        except TypeError:
            objects.append(o())
    physics = Physics()
    graphics = Graphics()

    # Scene
    scene = Scene(physics, objects, graphics)
    scene.instantiate_scene()
    scene.run_path(view=True,N=N,D=D,E=E)
    ticks.append(scene.physics.tick)
    # Get collision probability
    collision_prob += scene.physics.handlers['ball_goal'].data['colliding']
    
    return collision_prob, 1, ticks

def main():

    N,D,E = 10, 100, 0.95

    data = pd.read_json("../experiments/experiment3/data/cleaned_data.json")
    data['rt_norm'] = (data.rt-data.rt.mean())/data.rt.std()
    RT_y_mean = data.groupby('scene').rt.apply(np.mean)
    data = RT_y_mean

    # Collect scene parameter files for simulator
    scenedir = "../data/json/pilot3/"
    scene_files = [s_json for s_json in os.listdir(scenedir) if s_json.endswith('.json')]
    scene_args = {}
    for file in scene_files:
        with open(scenedir+file, 'r') as f:
            sargs = (json.loads(f.read()))
            scene_args[sargs['name'].split(".")[0]] = sargs
    RT_x = RT_y_mean.index.to_list()

    for x_ in RT_x:
        t = sim(scene_args[x_], int(N), D, E)[-1][0]
        print(t)

if __name__ == "__main__":
    main()