from numpy.random.mtrand import normal
from main import *
from scene import Scene
from itertools import product
from math import radians
from numpy.random import randint
import pymunk
from handlers import goal_ball

def generate_container_args(obj_args):
    '''
    obj_args -- Optional list of args for other objects in scene.
    '''
    num_containers = 5
    container_args = []
    opt_args = []
    ball_pos = obj_args[0][0]
    ball_by, ball_ty = ball_pos[1]+20, ball_pos[1]-20
    ball_rx, ball_lx = ball_pos[1]+20, ball_pos[1]-20
    ball_tr, ball_bl = (ball_rx,ball_ty), (ball_lx,ball_by)
    opt_args.append([ball_pos,1,1,ball_tr,ball_bl]) # Placeholder vals
    goal_pos = obj_args[1][0]
    goal_by, goal_ty  = goal_pos[1]+40, goal_pos[1]
    goal_rx, goal_lx = goal_pos[1]+40, goal_pos[1]-40
    goal_tr, goal_bl = (goal_rx,goal_ty), (goal_lx,goal_by)
    opt_args.append([goal_pos,1,1,goal_tr,goal_bl]) 
    objs = [Container]*num_containers

    # Sample container arguments until full
    while len(container_args) != num_containers:
        overlaps = False
        # Sample random position
        pos = randint(200,600), randint(200,800)
        # neg = -1 if randint(2) == 1 else 1

        # Sample random width and length
        l, w = normal(0,10), randint(40,80)

        # Compute area bounds of Container (y is inverted)
        b_y,t_y = pos[1]+l, pos[1]
        l_x,r_x = pos[0]-w-3, pos[0]+w+3

        # Get top left and bottom right for SAT
        tr,bl = (r_x,t_y), (l_x,b_y)

        # If the args are unique, add them to the list
        if [pos,w,l,tr,bl] not in container_args:
            container_args.append([pos,w,l,tr,bl])
        else:
            # If not unique, short-circuit loop and move on
            continue

        # Check if this container overlaps with the game border
        if (tr[0] < 20 or tr[0] > 780 or bl[0] > 780 or bl[0] < 20 or
            tr[1] < 20 or tr[1] > 980 or bl[1] > 980 or bl[1] < 20):
                # If so, short-circuit loop and move on
                container_args.pop(-1)
                continue
        
        # Check if this container overlaps with other containers
        for container in container_args[:-1]+opt_args:
            # Extract parameters of other container
            _, _, _, otr, obl = container
            # Map the contianer args onto a pymunk bounding box
            bb = pymunk.BB(left=bl[0],right=tr[0],top=bl[1],bottom=tr[1])
            obb = pymunk.BB(left=obl[0],right=otr[0],top=obl[1],bottom=otr[1])
            # Check for intersection
            if bb.intersects(obb):
                overlaps=True

        # If overlaps don't include in container arguments
        if overlaps:
            container_args.pop(-1)
    return objs, [ca[:3] for ca in container_args]

def generate_ball_args():
    pos = 400*normal(1,0.3), 100
    return [pos]

def generate_goal_args(b):
    pos = b[0][0]*normal(1,0.2), 1000
    return [pos]

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
        s = Scene(None, [Ball, Goal, o],[
            [(x_b,100)],
            [(x_g,1000)],
            [(x_o,y_o),w_o]
            ])
        if x_b == x_g:
            f = "../../images/stimuli/test/scene_test_ontop"+str(i)
        elif x_o == 400:
            f = "../../images/stimuli/test/scene_test_middle"+str(i)
        else:
           f = "../../images/stimuli/test/scene_test"+str(i) 
        s.forward(view=True,img_capture=True,fname=f)

def rotate_objs(name):
    pass

def rotate_obj(obj,theta):
        '''
        Rotates objects about a center
        '''
        obj.body.angle += radians(theta)

def generate_rotation(obj):
    name = "Container"
    neg = -1 if randint(2) == 1 else 1
    # Sample random width and length
    theta = randint(50)*neg
    # for obj in objects:
    if type(obj).__name__ == name:
        rotate_obj(obj,theta)

# Objects
objs = [Ball, Goal]

# Objects parameters
ball_args = generate_ball_args()
goal_args = generate_goal_args(ball_args)
scene_size = (800,1000)
o, p = generate_container_args([ball_args,goal_args])

params = [ball_args,goal_args]
objs += o
params += p
handlers = [(0, 1, goal_ball)]
s = Scene(handlers, objs, params,scene_size)
s.instantiate_scene([generate_rotation])
s.forward(view=True)
print(s.trajectories)