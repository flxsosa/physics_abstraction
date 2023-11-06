'''
File for scratch jobs and testing. Frequently overwritten.
'''
import numpy as np
from copy import deepcopy
from scene import Scene
from physics import Physics
from graphics import Graphics
from utility import load_object_arg_pairs,load_scene,scene_deepcopy
from random import choice
from stimuli_generation import scene_rt
import os
import json
import pandas as pd
import models
import tqdm
from pymunk.vec2d import Vec2d
import itertools
import video

def blank_scene(experiment, name=""):
    '''
    Returns a hardcoded "blank" scene with a preset screen size,
    preset border parameters, and no parameter definitions
    for objects.
    '''
    if experiment == 1:
        return {"name": f"{name}", 
                "screen_size": [800, 2000], 
                "objects": [
                    "Ball", 
                    "Block1", "Block2", "Block3", "Block4",
                    "PlinkoBorder", "BottomBorder"
                ], 
                "ball_args": [[550,57]], 
                "goal_args": [], 
                "container_args": [], 
                "bottom_border_args": [[10, 1980], [790, 1980]], 
                "plinko_border_args": [1992, 800]}
    elif experiment == 2:
        return {"name": f"{name}", 
                    "screen_size": [800, 1000], 
                    "objects": [
                        "Goal","Ball", "Container",
                        "PlinkoBorder", "BottomBorder"
                    ], 
                    "ball_args": [[400,57]], 
                    "goal_args": [[360,960]], 
                    "container_args": [
                        [[420,700],80,10,-30],
                        [[150,710],50,10,70]
                    ], 
                    "bottom_border_args": [[10, 980], [790, 980]], 
                    "plinko_border_args": [992, 800]}
    elif experiment == 3:
        return {"name": f"{name}", 
                    "screen_size": [800, 1000], 
                    "objects": [
                        "Goal","Ball", "Container",
                        "PlinkoBorder", "BottomBorder"
                    ], 
                    "ball_args": [[360,57]], 
                    "goal_args": [[360,960]], 
                    "container_args": [
                        [[500,700],80,10,-30],
                        [[150,710],50,10,70]
                    ], 
                    "bottom_border_args": [[10, 980], [790, 980]], 
                    "plinko_border_args": [992, 800]}

def generate_sections(w,h,n,m):
    '''
    Generate NxM evenly-spaced sections for a scene of
    size WxH. With respect to Pymunk geometry, the sections
    are returned going from top-left to bottom-right.

    :param w: Width of scene
    :param h: Height of scene
    :param n: Number of sections along width
    :param m: Number of sections along height
    '''
    offset = 300
    step_x = w / n
    step_y = (h-offset) / m
    xs = np.arange(0, w, step_x)
    xs += step_x / 2
    ys = np.arange(offset, h, step_y)
    ys += step_y / 2
    return list(xs), list(ys)

def run_scene_abstraction(scene_args, N=5,D=100,E=0.8, view=False):
    objects = []
    objs,args = load_object_arg_pairs(scene_args)
    for o,a in zip(objs, args):
        try:
            objects.append(o(*a))
        except TypeError:
            objects.append(o())

    s = Scene(objects)
    s.instantiate_scene()
    s.run_path(view=view,N=5,D=100,E=0.8)
    return s

def run_scene(scene_args, view=False):
    objects = []
    objs,args = load_object_arg_pairs(scene_args)
    for o,a in zip(objs, args):
        try:
            objects.append(o(*a))
        except TypeError:
            objects.append(o())
    s = Scene(objects, screen_size=scene_args['screen_size'])
    s.instantiate_scene()
    s.run(view=view)
    return s

def view_scene(s, view=False):
    f = open(s)
    scene_args = json.load(f)
    objects = []
    objs,args = load_object_arg_pairs(scene_args)
    for o,a in zip(objs, args):
        try:
            objects.append(o(*a))
        except TypeError:
            objects.append(o())
    s = Scene(objects, screen_size=scene_args['screen_size'])
    s.instantiate_scene()
    s.run_path(view=view)
    return s

def points(scene_args):
    offset = 200
    trace = run_scene(scene_args).trace
    if len(scene_args["container_args"]) == 0:
        trace = [x for x in trace if x[1] > 150]
        return [trace[i] for i in range(0,len(trace),20)]
    else:
        lowest_slide_pos = max(scene_args['container_args'], key=lambda x: x[0])[0]
        top_bound = lowest_slide_pos[1]
        bottom_bound = top_bound + offset
        trace = [x for x in trace if x[1] > top_bound+offset]
        return [trace[i] for i in range(0,len(trace),20)]

def update_scene(scene_args, slide_pos, slide_len, slide_angle):
    new_scene_args = scene_deepcopy(scene_args)
    slide_height = 0
    new_scene_args["container_args"].append([slide_pos,slide_len,slide_height,slide_angle])
    return new_scene_args

def passes_constraints(scene_args):
    # Must touch the bottom of the scene
    ss = run_scene(scene_args)
    goal_pos = [250, 1480] #ss.trace[-1]
    scene_args['objects'].append("Goal")
    scene_args['goal_args'].append(goal_pos)
    ss = run_scene(scene_args)
    sa = run_scene_abstraction(scene_args)
    scene_args['objects'].remove("Goal")
    scene_args['goal_args'] = []

    ss_coll = ss.physics.handlers['ball_goal'].data['colliding']
    sa_coll = sa.physics.handlers['ball_goal'].data['colliding']

    if ss.physics.tick >= 2000 or sa.physics.tick >= 2000:
        return False
    if ss_coll != True or sa_coll != True:
        return False
    
    return True

def generate_scenes(savedir):
    scene_library = []
    
    # Begin with a blank scene without slides
    new_scene = blank_scene()
    new_scene['objects'].append("Container")
    scene_library.append(new_scene)
    # Slide parameter ranges 
    slide_lens = [70]
    slide_thetas = [30,50,70,110,130,150]
    scene_count = 0
    scene_log = tqdm.tqdm(total=0, position=1, bar_format='{desc}')
    valid_scenes = 0
    # Iterate through the scene library
    for scene in scene_library:
        # Generate the set of points along which we can place a Slide
        #  and guarantee the Ball will collide with the Slide
        for point in points(scene):
            if point[1] < 450:
                continue
            if point[1] > 1000:
                continue
            # Iterate through the slide lengths
            for slide_len in slide_lens:
                # Iterate through the slide angles
                for theta in slide_thetas:
                    # Update the current scene with the new slide
                    scene_ = update_scene(scene, point, slide_len, theta)
                    scene_log.set_description_str(f'Current scene: {scene_count} | Scene library: {len(scene_library)} | Valid scenes {valid_scenes}')
                    scene_count += 1
                    # Check if the new scene satisfies our constraints
                    if passes_constraints(scene_):
                        scene_log.set_description_str(f'Current scene: {scene_count} | Scene library: {len(scene_library)} | Valid scenes {valid_scenes}')
                        scene_library.append(scene_)
                        if len(scene_['container_args']) > 1:
                            valid_scenes += 1 
                            with open(f"{savedir}test_scene_{scene_count}.json", "w") as outfile:
                                json.dump(scene_, outfile)
        
def test_scene(scene, goal_position = None):
    # Load scene
    scene = load_scene(scene)
    # Replace Goal at point
    for o in scene.objects:
        if o.name == "Goal":
            o.body.position = goal_position
    # Simulate
    scene.instantiate_scene()
    scene.run_path(True,*(35,200,0.9))
    print(scene.physics.tick)
    print(scene.ball_distance_traveled)

def variance_low(trace):
    xs = [x[0] for x in trace]
    ys = [y[1] for y in trace]
    return np.var(xs) < 500 or np.var(ys) < 10000

def generate_rt_scenes(scenedir):
    json_files = [pos_json for pos_json in os.listdir(scenedir) if pos_json.endswith('.json')]

    for scene in tqdm.tqdm(json_files, desc="Scene Loop"):
        f = open(scenedir+scene)
        scene_args = json.load(f)
        num_goal_positions = 30
        trace = run_scene(scene_args).trace
        trace = [x for x in trace if x[1] > 150]
        trace_indexes = np.round(np.linspace(0,len(trace)-1,num_goal_positions)).astype(int)
        trace = [trace[x] for x in trace_indexes]
        assert len(trace) == num_goal_positions
        samples = 100

        scene_args['objects'].append("Goal")
        # Starting position
        origin = trace[0]
        # Euclidean distances from the origin per point in trace
        euclidean_dist_from_origin = []
        results = pd.DataFrame({})

        # Iterate through points and compute runtimes and distances
        for point_idx,point in enumerate(tqdm.tqdm(trace[1:], desc="Point Loop", position=1, leave=False)):
            # Replace Goal at point
            scene_args["goal_args"] = [point]
            # Simulate
            model_results_simulation = models.simulation(scene_args,samples,0.01)
            runtime_simulation = model_results_simulation['simulation_time']
            dist_simulation = model_results_simulation['dist_ball_traveled']
            # comp_choice_simulation =  model_results_simulation['computation_choice']
            coll_simulation = model_results_simulation['collision_probability']
            
            model_results_abstraction = models.abstraction(scene_args,5,100,0.9,samples,0.01)
            runtime_abstraction = model_results_abstraction['simulation_time']
            dist_abstraction = model_results_abstraction['dist_ball_traveled']
            # comp_choice_abstraction = model_results_abstraction['computation_choice']
            coll_abstraction = model_results_abstraction['collision_probability']
            # Compute Euclidean distance from origin
            euclidean_dist_from_origin = origin.get_distance(point)

            for i in range(samples):
                df = pd.DataFrame({
                    "goal_x":[point[0]],
                    "goal_y":[point[1]],
                    "goal_point_idx":[point_idx],
                    "runtime_simulation":[runtime_simulation[i]],
                    "runtime_abstraction":[runtime_abstraction[i]],
                    "distance_from_origin":[euclidean_dist_from_origin],
                    "distance_simulation":[dist_simulation[i]],
                    "distance_abstraction":[dist_abstraction[i]],
                    "goal_collision_abstraction":[coll_abstraction[i]],
                    "goal_collision_simulation":[coll_simulation[i]]
                    })
                results = pd.concat([results,df])
        results = results.reset_index(drop=True)
        results.to_json(f"../data/rt_profiles_test_exp_comp_choice/{scene}")

def generate_rt_scene(scene_args, fname):
    num_goal_positions = 30
    trace = run_scene(scene_args).trace
    trace = [x for x in trace if x[1] > 150]
    trace_indexes = np.round(np.linspace(0,len(trace)-1,num_goal_positions)).astype(int)
    trace = [trace[x] for x in trace_indexes]
    assert len(trace) == num_goal_positions
    samples = 100

    # Starting position
    origin = trace[0]
    # Euclidean distances from the origin per point in trace
    euclidean_dist_from_origin = []
    results = pd.DataFrame({})

    # Iterate through points and compute runtimes and distances
    for point_idx,point in enumerate(tqdm.tqdm(trace[1:], desc="Point Loop", position=1, leave=False)):
        # Replace Goal at point
        scene_args["goal_args"] = [point]
        # with open(f"../data/scenes_test_exp/{fname}_{point_idx}.json", "w") as outfile:
        #     json.dump(scene_args, outfile)
        # Simulate
        model_results_simulation = models.simulation(scene_deepcopy(scene_args),samples,0.01)
        runtime_simulation = model_results_simulation['simulation_time']
        dist_simulation = model_results_simulation['dist_ball_traveled']
        coll_simulation = model_results_simulation['collision_probability']
        comp_choice_simulation =  model_results_simulation['computation_choice']

        model_results_abstraction = models.abstraction(scene_deepcopy(scene_args),5,100,0.9,samples,0.1)
        runtime_abstraction = model_results_abstraction['simulation_time']
        dist_abstraction = model_results_abstraction['dist_ball_traveled']
        coll_abstraction = model_results_abstraction['collision_probability']
        comp_choice_abstraction = model_results_abstraction['computation_choice']

        # Compute Euclidean distance from origin
        euclidean_dist_from_origin = origin.get_distance(point)

        for i in range(samples):
            df = pd.DataFrame({
                "goal_x":[point[0]],
                "goal_y":[point[1]],
                "goal_point_idx":[point_idx],
                "runtime_simulation":[runtime_simulation[i]],
                "runtime_abstraction":[runtime_abstraction[i]],
                "distance_from_origin":[euclidean_dist_from_origin],
                "distance_simulation":[dist_simulation[i]],
                "distance_abstraction":[dist_abstraction[i]],
                "goal_collision_abstraction":[coll_abstraction[i]],
                "goal_collision_simulation":[coll_simulation[i]],
                "comp_choice_simulation":[comp_choice_simulation[i]],
                "comp_choice_abstraction":[comp_choice_abstraction[i]]
                })
            results = pd.concat([results,df])
    results = results.reset_index(drop=True)
    results.to_json(f"../data/rt_profiles_test_exp_comp_choice/{fname}.json")

def mutate_scene(scene_args,fname):
    if np.random.uniform() < 0.5:
        shift_distance = np.random.normal()*100
        if shift_distance < -50:
            shift_distance = -50
        if shift_distance > 200:
            shift_distance = 200
        scene_args['goal_args'][0][0] += shift_distance
        scene_args['ball_args'][0][0] += shift_distance
        for container_arg in scene_args['container_args']:
            container_arg[0][0] += shift_distance
    min_x = 800
    max_x = 0
    for c in scene_args['container_args']:
        if c[0][0] < min_x:
            min_x = c[0][0]
        if c[0][0] > max_x:
            max_x = c[0][0]
    container_xs_1 = [100, min_x-100]
    container_xs_2 = [max_x+200, 700]
    container_ys = [200,500]

    new_pos_1 = choice(container_xs_1+container_xs_2), choice(container_ys)
    new_pos_2 = choice(container_xs_1+container_xs_2), choice(container_ys)
    print(type(new_pos_1[0]))
    scene_args['container_args'].append(
        [
        [*new_pos_1],
        choice(range(40,80)),
        10,
        choice(range(-70,70))
        ]
    )
    scene_args['container_args'].append(
        [
        [*new_pos_2],
        choice(range(40,80)),
        10,
        choice(range(-70,70))
        ]
    )
    run_scene(scene_args,True)
    with open(f"../data/scenes_test_exp_mutated/{fname}", "w") as outfile:
        json.dump(scene_args, outfile)

def generate_model_prediction(scene_args,scene_name,goal_idx):
    samples = 100

    # Starting position
    origin = Vec2d(*scene_args['ball_args'][0])
    # Euclidean distances from the origin per point in trace
    euclidean_dist_from_origin = []
    results = pd.DataFrame({})
    point = Vec2d(*scene_args['goal_args'][0])

    # Simulate
    model_results_simulation = models.simulation(scene_args,samples,0.01)
    runtime_simulation = model_results_simulation['simulation_time']
    dist_simulation = model_results_simulation['dist_ball_traveled']
    coll_simulation = model_results_simulation['collision_probability']
    comp_choice_simulation =  model_results_simulation['computation_choice']

    model_results_abstraction = models.abstraction(scene_args,5,100,0.9,samples,0.01)
    runtime_abstraction = model_results_abstraction['simulation_time']
    dist_abstraction = model_results_abstraction['dist_ball_traveled']
    coll_abstraction = model_results_abstraction['collision_probability']
    comp_choice_abstraction = model_results_abstraction['computation_choice']

    # Compute Euclidean distance from origin
    euclidean_dist_from_origin = origin.get_distance(point)

    for i in range(samples):
        df = pd.DataFrame({
            "goal_x":[point[0]],
            "goal_y":[point[1]],
            "goal_point_idx":[goal_idx],
            "runtime_simulation":[runtime_simulation[i]],
            "runtime_abstraction":[runtime_abstraction[i]],
            "distance_from_origin":[euclidean_dist_from_origin],
            "distance_simulation":[dist_simulation[i]],
            "distance_abstraction":[dist_abstraction[i]],
            "goal_collision_abstraction":[coll_abstraction[i]],
            "goal_collision_simulation":[coll_simulation[i]],
            "comp_choice_simulation":[comp_choice_simulation[i]],
            "comp_choice_abstraction":[comp_choice_abstraction[i]]
            })
        results = pd.concat([results,df])
    results = results.reset_index(drop=True)
    results.to_json(f"../data/rt_profiles_exp1/{scene_name}.json")

def main():
    # pass
    scenedir = "../data/scenes_test_exp/"
    # scenedir = "../data/json/pilot3/trial/"
    json_files = [pos_json for pos_json in os.listdir(scenedir) if pos_json.endswith('.json')]

    for scene_file in json_files:
        f = open(scenedir+scene_file)
        scene_args = json.load(f)
        num_goal_positions = 30
        trace = run_scene(scene_args).trace
        trace = [x for x in trace if x[1] > 150]
        trace_indexes = np.round(np.linspace(0,len(trace)-1,num_goal_positions)).astype(int)
        trace = [trace[x] for x in trace_indexes]
        assert len(trace) == num_goal_positions
        scene_args['objects'].append("Goal")

        # Iterate through points and compute runtimes and distances
        for point_idx,point in enumerate(tqdm.tqdm(trace[1:], desc="Point Loop", position=1, leave=False)):
            # Replace Goal at point
            scene_args["goal_args"] = [point]
            fname = scene_file.split(".")[0]
            fname += f"_trace_{point_idx}"

        # s["bottom_border_args"] = [[10, 980], [790, 980]]
        # s["plinko_border_args"] = [[992, 800]]
            video.make_video_from_args(fname,scene_args,"../data/videos/figures/")
    
    # view_scene("../data/scenes_test_exp/scene_1.json", True)



if __name__ == "__main__":
    main()
    

