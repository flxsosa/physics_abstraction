import os
from utility import load_scene_from_args, vid_from_img
import json
import random

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
        make_video(dir,file,_test=False)
        vid_from_img(fname,"/Users/lollipop/Desktop/tmp/")

def generate_types():
    dir = "/Users/lollipop/Desktop/tmp/"
    path_to_json = dir
    json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]
    for file in json_files:
        fname = file.split('.')[0]
        make_video(dir,file)
        vid_from_img(fname,"/Users/lollipop/Desktop/tmp/")
