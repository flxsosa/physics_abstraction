from simulation import Scene, Physics, Graphics
from objects import PlinkoBorder, BottomBorder
import os
from utility import load_scene,load_scene_from_args
import pandas as pd
import json
import pymunk
import numpy as np
import random
from helper import vid_from_img
from pilot4 import make_video

def main():
    dir = "/Users/lollipop/projects/physics_abstraction/data/json/pilot4/"
    json_files = ['comp_0.json','comp_1.json','comp_2.json','comp_3.json','comp_4.json','comp_5.json']
    for file in json_files[0:3]:
        fname = file.split(".")[0]
        with open(dir+file, 'r') as f:
            scene_args = json.loads(f.read())
        # scene = load_scene_from_args(scene_args)
        # scene.instantiate_scene()
        # scene.run(True,f"")
        make_video(file)
        vid_from_img(fname,"/Users/lollipop/projects/physics_abstraction/experiments/experiment4/img/stimuli/comprehension/")

    physics = Physics()
    graphics = Graphics()
    scene = Scene(physics,[PlinkoBorder(),BottomBorder()],graphics)

    scene.run()

if __name__ == "__main__":
    main()