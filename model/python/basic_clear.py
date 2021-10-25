from main import *
from scene import Scene
from handlers import end_state, goal_ball

# Scene
objects = [Ball,Goal,Tube]
h = [(0,1,goal_ball),(0,2,end_state)]

y = []
object_params = [ 
        [(400,100)],
        [(400,800)],
        [(400,300)]
        ]
        
s = Scene(h,objects,object_params)
s.forward()