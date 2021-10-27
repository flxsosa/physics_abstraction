from main import *
from scene import Scene
from itertools import product

x_ball = [100,400,700]
x_goal = [100,400,700]
x_obj = [100, 400]
y_obj = [200,500,800]
w_obj = [20,160]
obj = [Container, Tube]

def iterate_factors(**kwargs):
    i = 0

    objs = kwargs.get('obj',[])
    x_ball = kwargs.get('x_ball',[400])
    x_goal = kwargs.get('x_goal',[400])
    y_obj = kwargs.get('y_obj',[100])
    x_obj = kwargs.get('x_obj',[100])
    w_obj = kwargs.get('w_obj',[40])

    instances = list(product(objs, x_ball, x_goal, y_obj, x_obj, w_obj))
    tags = [
        "_ontop_"
    ]
    for i in range(len(instances)):
        o, x_b, x_g, y_o, x_o, w_o = instances[i]
        print(o, x_b, x_g, y_o, x_o, w_o)
        s = Scene(None, [Ball, Goal, o],[
            [(x_b,100)],
            [(x_g,1000)],
            [(x_o,y_o),w_o]
            ])
        if x_b == x_g:
            f = "../../images/stimuli/test/scene_test_ontop"+str(i)
        else:
           f = "../../images/stimuli/test/scene_test"+str(i) 
        s.forward(view=True,img_capture=True,fname=f)

iterate_factors(x_ball=x_ball,x_goal=x_goal,x_obj=x_obj,y_obj=y_obj,obj=obj)