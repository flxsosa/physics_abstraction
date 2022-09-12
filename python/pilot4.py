import os
from simulation import Graphics, Physics
from utility import load_scene,load_scene_from_args, vid_from_img, view_scenes_in_dir
import pandas as pd
import models
import json
import pymunk
import numpy as np
import random
import objects
from math import cos, sin, radians, sqrt
import seaborn as sns
import matplotlib.pyplot as plt
import itertools


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

def bb_from_ball_trace(trace):
    '''
    Construct bounding boxes around the ball's trace

    :param trace: The trace of the ball's position
    '''
    bounding_boxes = []
    for point in trace:
        # Construct a bounding box at each point the Ball will be, with width equivalent 
        #   to distance goal will possibly be shifted
        bb = pymunk.BB(left=point[0]-120,right=point[0]+120,top=point[1]-40,bottom=point[1]+40)
        bounding_boxes.append(bb)
    return bounding_boxes

def mutate_containers(scene_args,arg_range=(30,100)):
    container_args = scene_args['container_args']
    for idx in range(len(container_args)):
        scene_args['container_args'][idx][1] = np.random.uniform(*arg_range)
    return scene_args

def get_container_bb(c_arg):
    pos = c_arg[0]
    w = c_arg[1]
    l = c_arg[2]
    angle = c_arg[3]
    rads = radians(angle)
    x_1 = -w * cos(rads) - 0 * sin(rads)
    y_1 = -w * sin(rads) + 0 * cos(rads)
    x_2 = w * cos(rads) - 0 * sin(rads)
    y_2 = w * sin(rads) + 0 * cos(rads)
    x_1 = x_1+pos[0]
    y_1 = y_1+pos[1]
    x_2 = x_2+pos[0]
    y_2 = y_2+pos[1]
    left = min(x_1,x_2)
    right = max(x_1,x_2)
    top = min(y_1,y_2)
    bottom = max(y_1,y_2)
    return pymunk.BB(left=left,right=right,top=top,bottom=bottom)

def bb_overlap(min1,max1,min2,max2):
    return max1 >= min2 and max2 >= min1

def bb_intersect(bb1,bb2): 
    return bb_overlap(bb1.left,bb1.right, bb2.left,bb2.right) and bb_overlap(bb1.top, bb1.bottom, bb2.top,bb2.bottom)

def add_containers(scene_args,bbs,move_floor=False):
    new_scene_args = scene_args
    if 'Container' not in scene_args['objects']:
        scene_args['objects'].append('Container')
    num_containers = 3
    container_args = scene_args['container_args']
    if move_floor:
        goal_pos = scene_args['goal_args'][0]
        goal_y = goal_pos[1]
        pos1 = (10,goal_y+20)
        pos2 = (790,goal_y+20)
        new_scene_args['bottom_border_args'] = [pos1,pos2]
        new_scene_args['plinko_border_args'] = [goal_y+32]
        bottom_border = objects.BottomBorder(pos1,pos2)
        plinko_border = objects.PlinkoBorder(goal_y+32)
    else:
        plinko_border = objects.PlinkoBorder()
        bottom_border = objects.BottomBorder()
        new_scene_args['bottom_border_args'] = [(10,400),(790,400)]
        new_scene_args['plinko_border_args'] = [1000]
    # Sample container arguments until full
    while len(container_args) <= num_containers:
        overlaps = False
        # Sample random position
        pos = random.randint(200,600), random.randint(200,950)
        if move_floor:
            pos = pos[0],random.randint(200,int(goal_y+1))
        # Sample random width and length
        l, w = 0, random.randint(40,120)
        # Rotation
        rot = 90*np.random.normal(0,1)
        container_bb = get_container_bb([pos,w,l,rot])
        # Check if this container overlaps with the game border
        if bb_intersect(container_bb,bottom_border.components[1].bb):
                # If so, short-circuit loop and move on
                continue
        for line in plinko_border.components[1:]:
            if bb_intersect(container_bb,line.bb):
                    # If so, short-circuit loop and move on
                    continue
        # Check if container overlaps with trace
        for trace_bb in bbs:
            if bb_intersect(container_bb,trace_bb):
                overlaps=True
        # Check if this container overlaps with other containers
        for c_arg in container_args:
            # Extract parameters of other container
            other_container_bb = get_container_bb(c_arg)
            # Check for intersection
            if bb_intersect(container_bb,other_container_bb):
                overlaps=True
        # If overlaps don't include in container arguments
        if not overlaps:
            container_args.append([pos,w,l,rot])
    new_scene_args['container_args'] = container_args
    return new_scene_args

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
    return [trace[i] for i in sublist]

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
        bbs = bb_from_ball_trace(trace)
        # Remove the first twenty points of the trace
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
        bbs = bb_from_ball_trace(trace)
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

def make_video(dir,fname,alpha=False,region_test=False):
    # dir = "/Users/lollipop/projects/physics_abstraction/data/json/pilot4/"
    # savedir = "/Users/lollipop/Desktop/potential/"

    # Generate positive stimuli
    with open(dir+fname, 'r') as f:
        scene_args = json.loads(f.read())
    # Load the new scene
    scene = load_scene_from_args(scene_args,region_test)
    # Run the scene
    scene.instantiate_scene()
    if alpha:
        scene.graphics.draw_params['ball_alpha'] = True
    scene.run(view=True,fname=fname.split(".")[0],record=True)

def fix_stimuli(fname):
    dir = "/Users/lollipop/Desktop/tmp/"
    savedir = "/Users/lollipop/Desktop/potential/tmp/"
    # Generate positive stimuli
    with open(dir+fname, 'r') as f:
        scene_args = json.loads(f.read())
    # Load the new scene
    scene = load_scene_from_args(scene_args)
    # Run the scene
    scene.instantiate_scene()
    # scene.graphics.draw_params['trace'] = [(-20,-20)]
    scene.run(True)#,f"{savedir}{fname.split('.')[0]}")
    print(fname)
    # with open(f"{savedir}{fname.split('.')[0]}.json", 'w') as f:
    #     json.dump(scene_args, f)

def generate_pilot4_stimuli():
    dir = "/Users/lollipop/Desktop/tmp/"
    path_to_json = dir
    name = ''
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('negative.json') and name in pos_json]
    for file in json_files:
        fname = file.split(".")[0]
        make_video(dir,file)
        vid_from_img(fname,"/Users/lollipop/Desktop/tmp/")

def generate_pilot6_stimuli():
    dir = "/Users/lollipop/Desktop/tmp/"
    path_to_json = dir
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    for file in json_files:
        fname = file.split(".")[0]
        make_video(dir,file,region_test=False)
        vid_from_img(fname,"/Users/lollipop/Desktop/tmp/")

def add_bottom_segment(scene_args):
    new_scene_args = scene_args
    pos = random.randint(200,600), random.randint(200,950)
    # Sample random width and length
    l, w = 0, random.randint(40,120)
    # Rotation
    rot = 90*np.random.normal(0,1)
    container_bb = get_container_bb([pos,w,l,rot])

def generate_types():
    dir = "/Users/lollipop/Desktop/tmp/"
    path_to_json = dir
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    for file in json_files:
        fname = file.split('.')[0]
        make_video(dir,file)
        vid_from_img(fname,"/Users/lollipop/Desktop/tmp/")

def flip_movies():
    from moviepy.editor import VideoFileClip, vfx
    dir = "/Users/lollipop/Desktop/tmp/"
    savedir = dir+'flipped/'
    mp4_files = [pos_mp4 for pos_mp4 in os.listdir(dir) if pos_mp4.endswith('.mp4')]
    # print(mp4_files)
    idx = list(range(len(mp4_files)))
    mp4_samples = random.sample(idx, int(len(idx)/2))
    for idx in mp4_samples:
        file = mp4_files[idx]
        clip = VideoFileClip(dir+file)
        reversed_clip = clip.fx(vfx.mirror_x)
        reversed_clip.write_videofile(dir+file)  

def generate_stimuli_from_types_json(dir,savedir,negative):
    json_files = [pos_json for pos_json in os.listdir(dir) if pos_json.endswith('.json')]
    idx = 0
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
        bbs = bb_from_ball_trace(trace)
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
            # Shift the goal position
            mutated_scene_args = shift_goal(scene_args,point)
            # Run the scene
            with open(f"{savedir}{file.split('.')[0]}_goalpos_{idx}.json", 'w') as f:
                json.dump(mutated_scene_args, f)  

def scene_grid_containers(screen_size,sample_size=100,grid_step=100):
    x, y = screen_size
    # Get pixel values of area
    yi, yf = grid_step, y
    xi,xf = 0, x
    ys = list(range(yi,yf+grid_step,100))
    xs = list(range(xi,xf+grid_step,100))
    points = []
    for i in range(len(xs)-1):
        x1,x2 = xs[i],xs[i+1]
        for j in range(len(ys)-1):
            y1,y2 = ys[j],ys[j+1]
            points.append([(x1+x2)/2,(y1+y2)/2])
    length = grid_step
    samples = []
    for _ in range(sample_size):
        samples.append(np.random.choice(list(range(len(points))), np.random.randint(4,10)))
    container_args = []
    for sample in samples:
        c_args = []
        for s in sample:
            pos = points[s]
            rot = -45 if pos[0] > 400 else 45
            c_args.append([pos,length,0,rot])
        container_args.append(c_args)
    return container_args

def search_for_stimuli(savedir):
    scene_results = {}
    # Set up the scene
    scene_args = {}
    scene_size = [800,2000]
    scene_args['screen_size'] = scene_size
    scene_args['objects'] = ['Ball','Goal','BottomBorder','PlinkoBorder','Container']
    for i in range(100):
        # Add goal
        x = np.random.uniform(40,760)
        y = 1356
        scene_args['goal_args'] = [[x,y]]
        # Add ball
        x = np.random.uniform(40,760)
        y = 50
        scene_args['ball_args'] = [[x,y]]
        # Add borders
        scene_args['bottom_border_args'] = [[10,1380],[790,1380]]
        scene_args['plinko_border_args'] = [1392,800]
        # Add in containers
        container_args = scene_grid_containers(scene_size,sample_size=100)
        # Make scene
        for idx,c_args in enumerate(container_args):
            idx = idx + len(container_args)*i
            scene_args['name'] = f'{savedir}scene_{idx}'
            print(f"Running scene {scene_args['name']}")
            scene_results[scene_args['name']] = {'simulation':None,'abstraction':None}
            scene_args['container_args'] = c_args
            # Run simulation model
            sim_result = models.simulation(scene_args,num_samples=100,noise=0.02)
            abs_result = models.abstraction(scene_args=scene_args,num_samples=100)
            # Check that traces match
            traces_match = check_model_results(scene_args,sim_result,abs_result)
            if traces_match:
                print("Pass")
                with open(f"{scene_args['name']}.json", 'w') as f:
                    json.dump(scene_args, f)  
            else:
                print("Fail")

def check_model_results(scene_args,sim_result, abs_result):
    # Check that ball collides with goal in simulation
    if np.mean(sim_result['collision_probability']) < 0.90:
        return False
    # Check abstraction model
    if np.mean(abs_result['collision_probability']) < 0.90:
        return False
    # Check that both simulation traces collide with the same containers
    abs_result = models.abstraction(scene_args=scene_args,num_samples=1,noise=1)
    sim_result = models.simulation(scene_args,num_samples=1,noise=0.0)
    return abs_result['collision_trace'] == sim_result['collision_trace']

def main():
    generate_stimuli_from_types_json('/Users/lollipop/Desktop/new_types/','/Users/lollipop/Desktop/pilot7/',False)
    # search_for_stimuli('/Users/lollipop/Desktop/new_stims/')
    # generate_stimuli_from_types_json('/Users/lollipop/Desktop/new_stims/','/Users/lollipop/Desktop/new_types/',False)

if __name__ == "__main__":
    main()