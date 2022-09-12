# from cmath import cos, sin
from objects import *
from simulation import Scene, Physics, Graphics
import pandas as pd
import numpy as np
from numpy.random import normal
from math import degrees, cos, sin
import os
import json
from models import load_object_arg_pairs

def load_object_arg_pairs_2(scene_args):
    '''
    Instantiates objects via (object, argument) tuples

    :param scene_args: Arguments for scenes
    '''
    obj_map = {
        "Ball":Ball,
        "Container":Container,
        "Goal":Region,
        "PlinkoBorder":PlinkoBorder,
        "BottomBorder":BottomBorder,
        "Line":Line
    }
    objects = []
    object_args = []
    for obj in scene_args['objects']:
        if obj == "Ball":
            objects.append(obj_map[obj])
            object_args.append(scene_args["ball_args"])
        elif obj == "Goal":
            objects.append(obj_map[obj])
            object_args.append(scene_args["goal_args"])
        elif obj == "Container":
            for i in range(len(scene_args["container_args"])):
                objects.append(obj_map[obj])
                object_args.append(scene_args["container_args"][i])
        elif obj == "Line":
            for i in range(len(scene_args["line_args"])):
                objects.append(obj_map[obj])
                object_args.append(scene_args["line_args"][i])
        elif obj == "PlinkoBorder":
            objects.append(obj_map[obj])
            object_args.append([])
        elif obj == "BottomBorder":
            objects.append(obj_map[obj])
            object_args.append([])
        else:
            raise ValueError(f"Received an invalid value in load_objects: obj=={obj}")
    return objects, object_args

def abstraction_simulation_pp(scene_args,N=5,D=100,E=0.9):
    '''
    Deterministic physics simulator. Model outputs are end
    state of the scene and the number of ticks of one run 
    of a scene with no noise.

    :param scene_args: Arguments for scenes
    :param N: Number of forward passes of physics engine
    :param D: Length of path projection
    :oparam E: Cossim threshold for accepting abstraction
    '''
    ticks = []
    collision_prob = 0
    # Run scene
    objects = []
    objs,args = load_object_arg_pairs_2(scene_args)
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

def sim(scene_args,N=5,D=100,E=0.9,num_samples=1):
    '''
    Deterministic physics simulator. Model outputs are end
    state of the scene and the number of ticks of one run 
    of a scene with no noise.

    :param scene_args: Arguments for scenes
    :param N: Number of forward passes of physics engine
    :param D: Length of path projection
    :oparam E: Cossim threshold for accepting abstraction
    '''
    ns = normal(N,N/10,num_samples)
    ds = normal(D,D/10,num_samples)
    es = normal(E,E/100,num_samples)
    dist = {
        "collision_probability":[],
        "simulation_time":[]
        }
    for i in range(num_samples):
        n,d,e = ns[i], ds[i], es[i]
        coll_prob, _, sim_time = abstraction_simulation_pp(scene_args,N=n,D=d,E=e)
        dist['collision_probability'].append(coll_prob)
        dist['simulation_time'].append(sim_time)
        print(f"Running with N:{n}, D:{d}, E:{e}. Simtime: {sim_time}")

    return dist 

def convert_container_to_line(dictionary):
    '''
    Converts Container object arguments in a dictionary into Line object
    arguments.

    :param dictionary: Dictionary containing parameters to be changed
    '''
    line_args = []
    containers = dictionary['container_args']

    for c in containers:
        # Position
        c_pos = c[0]
        c_x = c_pos[0]
        c_y = c_pos[1]
        c_width = c[1]
        c_angle = c[3]

        point_a = ((c_x-c_width/2), c_y)
        point_b = ((c_x+c_width/2), c_y)

        line = [point_a,point_b,c_angle]
        line_args.append(line)

    dictionary['line_args'] = line_args
    while "Container" in dictionary['objects']:
        dictionary['objects'].remove('Container')
    dictionary.pop('container_args')

    dictionary['objects'].append("Line")

def main():
    # Director with relevant JSONs
    loaddir = "../../../Desktop/types/"
    print(os.listdir(loaddir))
    # Gather all of the json files in the directory of trial stimuli
    json_files = [pos_json for pos_json in os.listdir(loaddir) if pos_json.endswith('.json')]

    for file in json_files[1:2]:
        print(file)
        # Scene name
        scene_name = file.split(".")[0]
        # Open the JSON file
        with open(loaddir+file, 'r') as f:
            # Grab the scene arguments
            scene_args = json.loads(f.read())
            convert_container_to_line(scene_args)
        # Run scene
        objects = []
        objs,args = load_object_arg_pairs(scene_args)
        for o,a in zip(objs, args):
            try:
                print(o)
                print(*a)
                objects.append(o(*a))
                print(objects)
            except TypeError:
                objects.append(o())
        physics = Physics()
        graphics = Graphics(800,2000)

        # Scene
        scene = Scene(physics, objects, graphics)
        scene.instantiate_scene()
        scene.run(view=True)

if __name__ == "__main__":
    main()