from main import *
from scene import Scene
from handlers import end_state, goal_ball

# Scene
objects = [Ball,Goal]
h = [(0,1,goal_ball),(0,2,end_state)]

y = []
object_params = [ 
        [(600,967)],
        [(200,1000)]
        ]
        
s = Scene(h,objects,object_params)
s.forward(img_capture=True,fname="comp_2.jpg")