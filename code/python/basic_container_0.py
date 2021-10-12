from main import *
from scene import Scene
# Scene
objects = [Goal, Ball, Container]
object_params = [
    [(100,800)], 
    [(100,100)],
    [(100,200)]
    ]
s = Scene(objects,object_params)
s.forward()