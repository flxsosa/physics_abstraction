import os
from utility import load_scene,load_scene_from_args, vid_from_img
import pandas as pd
import json
import pymunk
import numpy as np
import random

def scene_trace(fname):
    # Get Ball position trace
    scene = load_scene(fname) # Load specific scene
    scene.instantiate_scene() # Instantiate objects in pymunk space
    scene.run(False) # Run simulation headless
    return scene.trace # Grab ball trace

def scene_rt(trace,fname,abstraction=False,params=(35,200,0.9)):
    # Starting position
    origin = trace[0] 

    # Runtimes to reach point from origin
    runtimes = []

    # Euclidean distances from the origin per point in trace
    distance_from_origin = []

    # Cumulative distance traveled from origin under pure simulation
    distance_travelled = []
    dx = 0 # Change in distance
    last_point = origin
    
    # Iterate through points and compute runtimes and distances
    for idx,point in enumerate(trace[1:]):
        # Compute cumulative distance traveled
        curr_point = point
        dx += last_point.get_distance(curr_point)
        last_point = curr_point
        distance_travelled.append(dx)

        # Compute Euclidean distance from origin
        distance_from_origin.append(origin.get_distance(point))

        # Load scene
        scene = load_scene(fname)
        # Replace Goal at point
        for o in scene.objects:
            if o.name == "Goal":
                o.body.position = point

        # Simulate
        scene.instantiate_scene()
        if abstraction:
            scene.run_path(False,*params)
        else:
            scene.run(False)

        # Record runtime
        runtimes.append(scene.physics.tick)
        
    return pd.DataFrame({
            "x":[x[0] for x in trace[1:]],
            "y":[x[1] for x in trace[1:]],
            "runtime":runtimes,
            "distance":distance_from_origin,
            "distance_cumulative":distance_travelled})

def bb_from_trace(trace):
    # Construct bounding boxes around the ball's trace
    bounding_boxes = []
    for point in trace:
        # Construct a bounding box at each point the Ball will be, with width equivalent 
        #   to distance goal will possibly be shifted
        bb = pymunk.BB(left=point[0]-80,right=point[0]+80,top=point[1]+20,bottom=point[1]-20)
        bounding_boxes.append(bb)
    return bounding_boxes

def mutate_containers(scene_args):
    container_args = scene_args['container_args']
    for idx in range(len(container_args)):
        scene_args['container_args'][idx][1] = np.random.uniform(30,100)
    return scene_args

def add_containers(scene_args,bbs):
    num_containers = 3 - len(scene_args['container_args'])
    candidate_args = []
    container_args = []
    # Sample container arguments until full
    while len(candidate_args) != num_containers:
        overlaps = False
        # Sample random position
        pos = random.randint(200,600), random.randint(200,950)
        # Sample random width and length
        l, w = np.random.normal(0,10), random.randint(40,120)
        # Compute area bounds of Container (y is inverted)
        b_y,t_y = pos[1]+l, pos[1]
        l_x,r_x = pos[0]-w-3, pos[0]+w+3
        tr,bl = (r_x,t_y), (l_x,b_y)
        container_bb = pymunk.BB(left=bl[0],right=tr[0],top=bl[1],bottom=tr[1])
        # Rotation
        rot = 90*np.random.normal(0,1)
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
        for bb in bbs:
            if bb.intersects(container_bb):
                overlaps=True
        # Check if this container overlaps with other containers
        for container in candidate_args[:-1]:
            # Extract parameters of other container
            _, _, _, _, otr, obl = container
            # Map the contianer args onto a pymunk bounding box
            bb = pymunk.BB(left=bl[0],right=tr[0],top=bl[1],bottom=tr[1])
            obb = pymunk.BB(left=obl[0],right=otr[0],top=obl[1],bottom=otr[1])
            # Check for intersection
            if bb.intersects(obb):
                overlaps=True
        # If overlaps don't include in container arguments
        if overlaps:
            candidate_args.pop(-1)
    container_args.append([ca[:4] for ca in candidate_args])
    return container_args[0]

def shift_goal(scene_args, point):
    scene_args['goal_args'] = [[point[0],point[1]]]
    return scene_args

def get_points(trace,N=15):
    '''
    Returns a sublist of N evenly-spaced
    elements from the original list.
    
    :param trace: Original list to be indexed
    :param N: The distance between each index
    '''
    origin = trace[0]
    cutoff = 0
    for idx, point in enumerate(trace):
        if abs(point[1] - origin[1]) > 200:
            cutoff = idx
            break
    sublist = np.round(np.linspace(cutoff, len(trace) - 1, N)).astype(int)
    return [origin] + [trace[i] for i in sublist]

def remove_first_twenty(trace):
    origin = trace[0]
    idx = 0
    for point in trace:
        if point[1]-origin[1] < 80:
            idx+=1
    new_trace = trace[idx:]
    return new_trace

def generate_positive_pilot4_stimuli():
    dir = "/Users/lollipop/Desktop/tmp/"
    savedir = "/Users/lollipop/Desktop/tmp/positive/"
    path_to_json = dir
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    # Generate positive stimuli
    for file in json_files:
        # Gather original scene arguments
        with open(dir+file, 'r') as f:
            scene_args = json.loads(f.read())
        # Extract position of the goal in the scene    
        goal_pos = scene_args['goal_args'][0]
        # Gather original trace
        trace = scene_trace(dir+file)
        # Gather bounding boxes for container generation
        bbs = bb_from_trace(trace)
        trace = remove_first_twenty(trace)
        # Append the goal position to the trace
        trace.append(goal_pos)
        # Gather goal positions
        goal_positions = get_points(trace)
        # Generate scene for each goal position placement
        for idx, point in enumerate(goal_positions):
            # Gather original scene arguments
            with open(dir+file, 'r') as f:
                scene_args = json.loads(f.read())
            # Mutate original containers
            mutated_scene_args = mutate_containers(scene_args)
            # Shift the goal position
            mutated_scene_args = shift_goal(mutated_scene_args,point)
            # Add new containers
            containers = add_containers(mutated_scene_args,bbs)
            for c in containers:
                mutated_scene_args['container_args'].append(c)
                mutated_scene_args['objects'].append('Container')
            # Load the new scene
            scene = load_scene_from_args(mutated_scene_args)
            # Run the scene
            scene.instantiate_scene()
            scene.graphics.draw_params['trace'] = [(-20,-20)]
            scene.run(True,f"{savedir}{file.split('.')[0]}_goalpos_{idx}")
            with open(f"{savedir}{file.split('.')[0]}_goalpos_{idx}.json", 'w') as f:
                json.dump(mutated_scene_args, f)

def generate_negative_pilot4_stimuli():
    dir = "/Users/lollipop/Desktop/tmp/negative/"
    savedir = "/Users/lollipop/Desktop/tmp/negative/"
    path_to_json = dir
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

    # Generate positive stimuli
    for file in ['stim_2_goalpos_2_negative.json']:
        # Gather original scene arguments
        with open(dir+file, 'r') as f:
            scene_args = json.loads(f.read())
        trace = scene_trace(dir+file)
        bbs = bb_from_trace(trace)
        # Extract position of the goal in the scene    
        goal_pos = scene_args['goal_args'][0]
        bit = 1 if random.uniform(0,1) > 0.5 else -1
        goal_pos[0] += bit*120 
        mutated_scene_args = shift_goal(scene_args,goal_pos)
        # Mutate original containers
        mutated_scene_args = mutate_containers(scene_args)
        # Add new containers
        containers = add_containers(mutated_scene_args,bbs)
        for c in containers:
            mutated_scene_args['container_args'].append(c)
            mutated_scene_args['objects'].append('Container')
        # Load the new scene
        scene = load_scene_from_args(mutated_scene_args)
        # Run the scene
        scene.instantiate_scene()
        scene.graphics.draw_params['trace'] = [(-20,-20)]
        scene.run(True,f"{savedir}{file.split('.')[0]}_negative")
        with open(f"{savedir}{file.split('.')[0]}_negative.json", 'w') as f:
            json.dump(mutated_scene_args, f)

def make_video(dir,fname):
    # dir = "/Users/lollipop/projects/physics_abstraction/data/json/pilot4/"
    # savedir = "/Users/lollipop/Desktop/potential/"

    # Generate positive stimuli
    with open(dir+fname, 'r') as f:
        scene_args = json.loads(f.read())
    # Load the new scene
    scene = load_scene_from_args(scene_args)
    # Run the scene
    scene.instantiate_scene()
    # scene.graphics.draw_params['ball_alpha'] = True
    scene.run(True,fname.split(".")[0])

def fix_stimuli(fname):
    dir = "/Users/lollipop/Desktop/potential/tmp/"
    savedir = "/Users/lollipop/Desktop/potential/tmp/"

    # Generate positive stimuli
    with open(dir+fname, 'r') as f:
        scene_args = json.loads(f.read())
    # Load the new scene
    scene = load_scene_from_args(scene_args)
    # Run the scene
    scene.instantiate_scene()
    scene.graphics.draw_params['trace'] = [(-20,-20)]
    scene.run(True,f"{savedir}{fname.split('.')[0]}")
    print(fname)
    with open(f"{savedir}{fname.split('.')[0]}.json", 'w') as f:
        json.dump(scene_args, f)

def generate_pilot4_stimuli():
    dir = "/Users/lollipop/projects/physics_abstraction/data/json/pilot4/trial/"
    path_to_json = dir
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    for file in json_files:
        fname = file.split(".")[0]
        make_video(dir,file)
        vid_from_img(fname,"/Users/lollipop/Desktop/tmp/")

def flip_movies():
    dir = "/Users/lollipop/Desktop/tmp/"
    savedir = dir+'flipped/'
    mp4_files = [pos_mp4 for pos_mp4 in os.listdir(dir) if pos_mp4.endswith('.mp4')]
    # print(mp4_files)
    idx = list(range(len(mp4_files)))
    mp4_samples = random.sample(idx, int(len(idx)/2))
    from moviepy.editor import VideoFileClip, vfx
    for idx in mp4_samples:
        file = mp4_files[idx]
        clip = VideoFileClip(dir+file)
        reversed_clip = clip.fx(vfx.mirror_x)
        reversed_clip.write_videofile(dir+file)  
