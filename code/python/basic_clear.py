from main import *
from scene import Scene
# Scene
objects = [Goal, Ball]
object_params = [
    [(100,800)], 
    [(100,100)]
    ]
s = Scene(objects,object_params)
s.forward()