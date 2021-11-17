from main import *
from scene import Scene
from itertools import product
from math import radians
from numpy.random import randint
from stimuli import *
import pymunk

objs = [Ball, Goal, Platform, Container]
params = []
ball_args = [(700,100),10]
goal_args = generate_goal_args()
plat_args = []
container_args = [(600,170)]
params.append(ball_args)
params.append(goal_args)
params.append(plat_args)
params.append(container_args)

s = Scene(None, objs, params)
s.instantiate_hamrick()
s.forward(view=True)