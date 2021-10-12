'''
Given a scene s, extract the objects obj_s, compute their distances, 
use the relevant distances d in a weighted sum to compute a 
predicted response time rt
'''
from main import *
from scene import Scene
from math import sqrt
from numpy.random import normal
import numpy as np
import matplotlib.pyplot as plt

# Constants
samples = 1000
obj_parse_constant = 200
dist_parse_constant = 2
recognition_constant = 200
# cutoff = int(200*normal(0,0.1,samples))

def response_time(scene):
    # Instantiate the scene objects with their arguments
    scene.instantiate_scene()
    # Extract the objects
    scene_objs = {type(o).__name__:o for o in scene.objects}
    #Compute distance
    print(dist_euclid(scene_objs["Ball"], scene_objs["Goal"]))
    # Reset scene objects
    scene.reset()

def dist_euclid(obj1, obj2):
    d = 0
    for i in range(len(obj1.init_position)):
        d += (obj1.init_position[i] - obj2.init_position[i])**2
    return math.sqrt(d)*dist_parse_constant

def clear_path(obj1, obj2):
    return dist_euclid(obj1,obj2)*normal(1,0.1,samples)

def container(obj1,obj2):
    return dist_euclid(obj1,obj2)*normal(1,0.1,samples)

def parse_scene(scene):
    return obj_parse_constant*len(scene.objects)*normal(1,0.1,samples)

def plot_rt_scene(s):
    s.instantiate_scene()
    objs = {type(o).__name__:o for o in s.objects}
    rt = clear_path(objs["Ball"], objs["Goal"])
    rt += parse_scene(s)
    s.reset()
    plt.hist(rt, 30, density=True)
    plt.title("Response Times")
    plt.xlabel("RT (in milliseconds)")
    plt.ylabel("P(RT)")
    plt.show()

def plot_rt_sim_cp():
    x = list(range(701))
    y = list(i*normal(1,0.1,samples)+2*obj_parse_constant*normal(1,0.1,samples) for i in x)
    plt.plot(x,y)
    plt.title("Pure Simulation Model:\nClear Paths")
    plt.ylabel("RT (in milliseconds)")
    plt.xlabel("Distance Between Ball and Goal")
    # plt.show()
    plt.savefig("plot_cp_distance.png",dpi=300)
    plt.clf()

def plot_rt_heur_cp():
    x = list(range(701))
    y = list(2*obj_parse_constant*normal(1,0.1,samples) for i in x)
    plt.plot(x,y)
    plt.title("Pure Heuristic Model:\nClear Paths")
    plt.ylabel("RT (in milliseconds)")
    plt.xlabel("Distance Between Ball and Goal")
    # plt.show()
    plt.savefig("plot_heur_cp_distance.png",dpi=300)
    plt.clf()

def plot_rt_mix_cp():
    distance = 701
    xy = {i:[] for i in list(range(distance))}
    for i in range(samples):
        cutoff = int(200*normal(1,0.1))
        for i in range(distance):
            if i < cutoff:
                xy[i].append(2*obj_parse_constant*normal(1,0.1))
            else:
                xy[i].append(i*normal(1,0.1)+2*obj_parse_constant*normal(1,0.1))
    x = list(xy.keys())
    y = list(xy.values())
    plt.plot(x,y)
    plt.title("Mixed Model:\nClear Paths")
    plt.ylabel("RT (in milliseconds)")
    plt.xlabel("Distance Between Ball and Goal")
    plt.savefig("plot_mix_cp_distance.png",dpi=300)
    plt.clf()

def plot_rt_sim_cont():
    x = list(range(701))
    y = list(i*normal(1,0.1,samples)+
        2*obj_parse_constant*normal(1,0.1,samples) for i in x)
    plt.plot(x,y)
    plt.title("Pure Simulation Model:\nContainers")
    plt.ylabel("RT (in milliseconds)")
    plt.xlabel("Distance Between Ball and Goal")
    # plt.show()
    plt.savefig("plot_cont_distance.png",dpi=300)
    plt.clf()

def plot_rt_heur_cont():
    x = list(range(701))
    y = list(2*obj_parse_constant*normal(1,0.1,samples)+
        recognition_constant*normal(1,0.1,samples) for i in x)
    plt.plot(x,y)
    plt.title("Pure Heuristic Model:\nContainers")
    plt.ylabel("RT (in milliseconds)")
    plt.xlabel("Distance Between Ball and Goal")
    # plt.show()
    plt.savefig("plot_heur_cont_distance.png",dpi=300)
    plt.clf()

def plot_rt_mix_cont():
    distance = 701
    xy = {i:[] for i in list(range(distance))}
    for i in range(samples):
        cutoff = int(200*normal(1,0.1))
        for i in range(distance):
            if i < cutoff:
                xy[i].append(2*obj_parse_constant*normal(1,0.1)+
                            recognition_constant*normal(1,0.1))
            else:
                xy[i].append(i*normal(1,0.1)+2*obj_parse_constant*normal(1,0.1))
    x = list(xy.keys())
    y = list(xy.values())
    plt.plot(x,y)
    plt.title("Mixed Model:\nContainers")
    plt.ylabel("RT (in milliseconds)")
    plt.xlabel("Distance Between Ball and Goal")
    plt.savefig("plot_mix_cont_distance.png",dpi=300)
    plt.clf()

plot_rt_sim_cont()
plot_rt_heur_cont()
plot_rt_mix_cont()