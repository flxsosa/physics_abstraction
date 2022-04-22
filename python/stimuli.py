from numpy.random.mtrand import normal, randint, uniform
import pymunk
from handlers import goal_ball
import json

def generate_container_args(n,nc,ball_args,goal_args,line_args=None):
    '''
    Generate a list of arguments for containers to be added to a Scene.

    :param n: Number of samples of container argument sets.
    :param nc: Number of individual container arguments to be generated per sample
               (i.e. how many containers you want per Scene).
    :param ball_args: Ball arguments, to prevent containers from overlapping with Ball.
    :param goal_args: Goal arguments, to prevent containers from overlapping with Gaol.
    '''
    num_containers = nc
    container_args = []
    opt_args = []
    for i in range(n):
        candidate_args = []
        ball_pos = ball_args[i]
        ball_by, ball_ty = ball_pos[1]+20, ball_pos[1]-20
        ball_rx, ball_lx = ball_pos[1]+20, ball_pos[1]-20
        ball_tr, ball_bl = (ball_rx,ball_ty), (ball_lx,ball_by)

        opt_args.append([ball_pos,1,1,1,ball_tr,ball_bl]) # Placeholder vals

        goal_pos = goal_args[i]
        goal_by, goal_ty  = goal_pos[1]+40, goal_pos[1]
        goal_rx, goal_lx = goal_pos[1]+40, goal_pos[1]-40
        goal_tr, goal_bl = (goal_rx,goal_ty), (goal_lx,goal_by)

        opt_args.append([goal_pos,1,1,1,goal_tr,goal_bl]) 

        # Sample container arguments until full
        while len(candidate_args) != num_containers:
            overlaps = False
            # Sample random position
            pos = randint(200,600), randint(200,950)
            # Sample random width and length
            l, w = normal(0,10), randint(40,120)

            # Compute area bounds of Container (y is inverted)
            b_y,t_y = pos[1]+l, pos[1]
            l_x,r_x = pos[0]-w-3, pos[0]+w+3
            tr,bl = (r_x,t_y), (l_x,b_y)

            # Rotation
            rot = 90*normal(0,1)

            # If the args are unique, add them to the list
            if [pos,w,l,rot,tr,bl] not in candidate_args:
                candidate_args.append([pos,w,l,rot,tr,bl])
            else:
                # If not unique, short-circuit loop and move on
                continue

            # Check if this container overlaps with the game border
            if (tr[0] < 20 or tr[0] > 780 or bl[0] > 780 or bl[0] < 20 or
                tr[1] < 20 or tr[1] > 980 or bl[1] > 980 or bl[1] < 20):
                    # If so, short-circuit loop and move on
                    candidate_args.pop(-1)
                    continue
            
            # Check if this container overlaps with other containers
            for container in candidate_args[:-1]+opt_args:
                # Extract parameters of other container
                _, _, _, _, otr, obl = container
                # Map the contianer args onto a pymunk bounding box
                bb = pymunk.BB(left=bl[0],right=tr[0],top=bl[1],bottom=tr[1])
                obb = pymunk.BB(left=obl[0],right=otr[0],top=obl[1],bottom=otr[1])
                # lbb = pymunk.BB(left=line_args[0][0][0],right=line_args[0][1][0],top=line_args[0][1][0],bottom=line_args[0][1][1])
                # Check for intersection
                if bb.intersects(obb):
                    overlaps=True
                # elif bb.intersects(lbb):
                #     overlaps=True

            # If overlaps don't include in container arguments
            if overlaps:
                candidate_args.pop(-1)
        
        container_args.append([ca[:4] for ca in candidate_args])
    
    return container_args

def generate_ball_args(n, conditions):
    '''
    Generate arguments for a Ball in a Scene.

    :param n: Batch size in case it speeds up stimuli generation (it might not).
    :param conditions: User-defined dictionary of special conditions arguments
                       should meet. Useful for condition-specific stimuli creation.
    '''
    xpos = randint(20,780,n) 
    cond_map = {
        "low":(650,950),
        "med":(350,600),
        "med_high":(150,300),
        "high":(50,300)
    }
    if conditions:
        ypos = uniform(*cond_map[conditions['rt']],n)
    else:   
        ypos = uniform(0,1000,n)           
    return [(x,y) for x,y in zip(xpos,ypos)]

def generate_goal_args(n,conditions):
    '''
    Generate arguments for a Ball in a Scene.

    :param n: Batch size in case it speeds up stimuli generation (it might not).
    :param conditions: User-defined dictionary of special conditions arguments
                       should meet. Useful for condition-specific stimuli creation.
    '''
    if conditions:
        if conditions['sp']==True and conditions['bgc']==True:
            xpos = conditions['ball_x']
        elif conditions['sp']==True and conditions['bgc']==False:
            xpos = x_away_from_ball(conditions['ball_x'],n)
        else:
            xpos = randint(40,760,n)
    else:
        xpos = randint(40,760,n)
    ypos = [1000]*n
    return [(x,y) for x,y in zip(xpos,ypos)]

def x_away_from_ball(x,n):
    '''
    Convenience function for generating x coordinates that are not the same
    as a given x coordinate (e.g. making sure a Ball is not right above a Goal)

    :param x: The coordinate to avoid.
    :param n: Batch size.
    '''
    xs = []
    for x_ in x:
        if uniform() < 0.5:
            if x_ > 140:
                xs.append(randint(40,x_))
            else:
                xs.append(760)
        else:
            if x_ < 710:
                xs.append(randint(x_,760))
            else:
                xs.append(40)
    assert len(xs) == n
    return xs

def generate_scene():
    # Objects
    handlers = [(0, 1, goal_ball)]
    scene_size = (800,1000)
    objs = [Ball, Goal]
    # Objects parameters
    ball_args = generate_ball_args()
    goal_args = generate_goal_args(ball_args)
    o, p = generate_container_args([ball_args,goal_args])
    params = [ball_args,goal_args]
    objs += o
    params += p
    s = Scene('',handlers, objs, params,scene_size)
    return s

def generate_simple_scene():
    # Objects
    handlers = [(0, 1, goal_ball)]
    scene_size = (800,1000)
    objs = [Ball, Goal,Container,Container]
    # Objects parameters
    ball_args = [(500,100)]
    goal_args = [(100,1000)]
    container_args = [(100,500),40,80]
    container2_args = [(100,800),40,80]
    params = [ball_args,goal_args,container_args,container2_args]
    s = Scene('',handlers, objs, params,scene_size)
    return s

def record_scene(scene,*args):
    '''
    Record beginning arguments and relevant end states for simulation
    into a dictionary to be saved into JSON in downstream functions.
    '''
    record = {}
    dir="../data/json/test/"
    record['name'] = args[0][0]
    record['collision_prob'] = scene.num_collisions/100
    record['collision'] = scene.goal_ball_collision
    record['screen_size'] = args[0][-1]
    record['tick'] = int(scene._tick)
    record['objects'] = [o.__name__ for o in scene._objects]
    record['object_params'] = scene._object_args
    with open(dir+args[0][0]+'.json', 'w') as f:
        json.dump(record, f)

def generate_stims():
    # Binning parameters
    tick_bins = [(0,301),(301,501),(501,801)]
    num_per_bin = 5

    # Bin dictionary
    bins = {
        'low_no':5,
        'low_yes':5,
        'med_no':5,
        'med_yes':0,
        'high_no':5,
        'high_yes':0
    }

    while True:
        print(list(map(lambda x: x, bins.values())))
        dict_keys = bins.keys()
        scene = generate_scene()
        scene.forward_stochastic(False)
        # First range
        if int(scene._tick) in range(*tick_bins[0]):
            if scene.num_collisions > 90 and 'low_yes' in dict_keys and bins['low_yes']<num_per_bin:
                name = 'low_yes'+str(bins['low_yes'])
                bins['low_yes']+=1
                scene.record_args([name,scene.coll_handlers,
                                   scene._objects, scene._object_args,
                                   (scene.width,scene.height)])
            elif scene.num_collisions < 10 and 'low_no' in dict_keys and bins['low_no']<num_per_bin:
                name = 'low_no'+str(bins['low_no'])
                bins['low_no']+=1
                scene.record_args([name,scene.coll_handlers,
                                   scene._objects, scene._object_args,
                                   (scene.width,scene.height)])
        # Second range
        elif int(scene._tick) in range(*tick_bins[1]):
            if scene.num_collisions > 90 and 'med_yes' in dict_keys and bins['med_yes']<num_per_bin:
                name = 'med_yes'+str(bins['med_yes'])
                bins['med_yes']+=1
                scene.record_args([name,scene.coll_handlers,
                                   scene._objects, scene._object_args,
                                   (scene.width,scene.height)])
            elif scene.num_collisions < 10 and 'med_no' in dict_keys and bins['med_no']<num_per_bin:
                name = 'med_no'+str(bins['med_no'])
                bins['med_no']+=1
                scene.record_args([name,scene.coll_handlers,
                                   scene._objects, scene._object_args,
                                   (scene.width,scene.height)])
        # Third range
        elif int(scene._tick) in range(*tick_bins[2]):
            if scene.num_collisions > 90 and 'high_yes' in dict_keys and bins['high_yes']<num_per_bin:
                name = 'high_yes'+str(bins['high_yes'])
                bins['high_yes']+=1
                scene.record_args([name,scene.coll_handlers,
                                   scene._objects, scene._object_args,
                                   (scene.width,scene.height)])
            elif scene.num_collisions < 10 and 'high_no' in dict_keys and bins['high_no']<num_per_bin:
                name = 'high_no'+str(bins['high_no'])
                bins['high_no']+=1
                scene.record_args([name,scene.coll_handlers,
                                   scene._objects, scene._object_args,
                                   (scene.width,scene.height)])
        else:
            continue

        if all(list(map(lambda x: x==num_per_bin, bins.values()))):
            break

def generate_scene_img(img=True,movie=False):
    obj_map = {
        "Ball":Ball,
        "Container":Container,
        "Goal":Goal
    }
    dir = "../data/json/pilot2/"
    w_dir = "../data/images/abstraction/"
    import os, json
    handlers = [(0, 1, goal_ball)]

    path_to_json = dir
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    for file in json_files:
        with open(dir+file, 'r') as f:
            scene = json.loads(f.read())
            print(scene)
            print(scene['objects'])
            objs = [obj_map[o] for o in scene['objects']]
            s = Scene(scene['name'],handlers,objs,scene['object_params'],scene['screen_size'])
            s.forward(True,img_capture=True,movie_capture=False,alpha_capture=False,dir=w_dir)

def generate_scene_img_alpha(img=False,movie=True):
    '''
    Generates movies of stimuli with ball having fading alpha values
    '''
    obj_map = {
        "Ball":Ball,
        "Container":Container,
        "Goal":Goal
    }
    path_to_json = "../data/json/pilot2/"
    w_dir = "../stimuli/test2/"
    import os, json
    handlers = [(0, 1, goal_ball)]

    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    for file in json_files:
        with open(path_to_json+file, 'r') as f:
            scene = json.loads(f.read())
            objs = [obj_map[o] for o in scene['objects']]
            s = Scene(scene['name']+"_alpha",handlers,objs,scene['object_params'],scene['screen_size'])
            s.forward(True,img_capture=False,movie_capture=True,alpha_capture=True,dir=w_dir)

def generate_scene_from_json():
    obj_map = {
        "Ball":Ball,
        "Container":Container,
        "Goal":Goal
    }
    dir = "../data/json/test/"
    import json
    import os
    handlers = [(0, 1, goal_ball)]

    path_to_json = dir
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    for file in json_files:
        with open(dir+file, 'r') as f:
            scene = json.loads(f.read())
            objs = [obj_map[o] for o in scene['objects']]
            s = Scene(scene['name'],handlers,objs,scene['object_params'],scene['screen_size'])
            print(scene['collision_prob'])
            s.forward()