import json
import math
import numpy as np
import os
import objects
import pandas as pd
import pymunk
import random
import utility


def scene_trace(fname):
    # Get Ball position trace
    scene = utility.load_scene(fname) # Load specific scene
    scene.instantiate_scene() # Instantiate objects in pymunk space
    scene.run(False) # Run simulation headless
    return scene.trace # Grab ball trace


def scene_rt(trace,fname,params=(35,200,0.9)):
    # Starting position
    origin = trace[0] 
    # Runtimes to reach point from origin
    runtimes_simulation = []
    runtimes_abstraction = []
    # Euclidean distances from the origin per point in trace
    euclidean_dist_from_origin = []
    # Cumulative distance traveled from origin under pure simulation
    euclidean_dist_traveled_simulation = []
    euclidean_dist_traveled_abstraction = []
    # Iterate through points and compute runtimes and distances
    for _, point in enumerate(trace[1:]):
        # Compute Euclidean distance from origin
        euclidean_dist_from_origin.append(origin.get_distance(point))
        # Load scene
        scene = utility.load_scene_from_args(fname)
        # Replace Goal at point
        for o in scene.objects:
            if o.name == "Goal":
                o.body.position = point
        # Simulate
        model_results = models.simulation(sc)
        scene.instantiate_scene()
        scene.run(False)
        euclidean_dist_traveled_simulation.append(scene.ball_distance_traveled)

        # Record runtime
        runtimes_simulation.append(scene.physics.tick)
    # Iterate through points and compute runtimes and distances
    for _, point in enumerate(trace[1:]):
        # Load scene
        scene = utility.load_scene_from_args(fname)
        # Replace Goal at point
        for o in scene.objects:
            if o.name == "Goal":
                o.body.position = point
        # Simulate
        scene.instantiate_scene()
        scene.run_path(False, *params)
        if scene.ball_distance_traveled > 5000:
            print(f"{point} produces RT {scene.ball_distance_traveled}")
        euclidean_dist_traveled_abstraction.append(scene.ball_distance_traveled)
        # Record runtime
        runtimes_abstraction.append(scene.physics.tick)
    return pd.DataFrame({
            "goal_x":[x[0] for x in trace[1:]],
            "goal_y":[x[1] for x in trace[1:]],
            "goal_point_idx":[x for x in range(len(trace[1:]))],
            "runtime_simulation":runtimes_simulation,
            "runtime_abstraction":runtimes_abstraction,
            "distance_from_origin":euclidean_dist_from_origin,
            "distance_traveled_simulation":euclidean_dist_traveled_simulation,
            "distance_traveled_abstraction":euclidean_dist_traveled_abstraction})


def get_points(trace,N=15):
    """Returns a sublist of N evenly-spaced elements from the original list.
    
    Args:
        trace: Original list to be indexed
        N: The distance between each index
    """
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


def bb_from_ball_trace(trace):
    """Construct bounding boxes around the ball's trace

    Args:
        trace: The trace of the ball's position
    """
    bounding_boxes = []
    for point in trace:
        # Construct a bounding box at each point the Ball will be, with width equivalent 
        #   to distance goal will possibly be shifted
        bb = pymunk.BB(left=point[0]-120,right=point[0]+120,top=point[1]-40,bottom=point[1]+40)
        bounding_boxes.append(bb)
    return bounding_boxes


def get_container_bb(c_arg):
    pos = c_arg[0]
    w = c_arg[1]
    l = c_arg[2]
    angle = c_arg[3]
    x_1 = -w * math.cos(rads) - 0 * math.sin(rads)
    y_1 = -w * math.sin(rads) + 0 * math.cos(rads)
    x_2 = w * math.cos(rads) - 0 * math.sin(rads)
    y_2 = w * math.sin(rads) + 0 * math.cos(rads)
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
    return (bb_overlap(bb1.left,bb1.right,bb2.left,bb2.right) and
            bb_overlap(bb1.top, bb1.bottom, bb2.top,bb2.bottom))


def mutate_containers(scene_args,arg_range=(30,100)):
    container_args = scene_args['container_args']
    for idx in range(len(container_args)):
        scene_args['container_args'][idx][1] = np.random.uniform(*arg_range)
    return scene_args


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
        print(*scene_args['bottom_border_args'])
        print(*scene_args['plinko_border_args'])
        plinko_border = objects.PlinkoBorder(*scene_args['plinko_border_args'])
        bottom_border = objects.BottomBorder(*scene_args['bottom_border_args'])
    #     new_scene_args['bottom_border_args'] = [(10,400),(790,400)]
    #     new_scene_args['plinko_border_args'] = [1000]
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


def generate_stimuli_json(dir,savedir,negative):
    """Generates a stimuli from a scene.

    Args:
        dir: Directory containing JSON configs of scene types
        savdir: Directory to save resulting scenes to
    """
    # Gather original scene arguments
    with open(dir+file, 'r') as f:
        scene_args = json.loads(f.read())
    mutated_scene_args = add_containers(mutated_scene_args, bbs)
    mutated_scene_args['name'] = f"{file.split('.')[0]}_goalpos_{idx}"
    # Run the scene
    if negative:
        name = f"{savedir}{file.split('.')[0]}_goalpos_{idx}_negative.json"
    else:
        name = f"{savedir}{file.split('.')[0]}_goalpos_{idx}.json"
    with open(name, 'w') as f:
        json.dump(mutated_scene_args, f)  


def generate_stimuli_from_types_json(dir,savedir,negative,N=15):
    """Generates a series of stimuli from a scene type.

    Args:
        dir: Directory containing JSON configs of scene types
        savdir: Directory to save resulting scenes to
        negative: Boolean flag for whether scene depicts negative scene or not
        N: How many points along the trace to sample
    """
    json_files = [
        pos_json
        for pos_json
        in os.listdir(dir)
        if pos_json.endswith('.json')]
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
        goal_positions = get_points(trace, N)
        # Generate scene for each goal position placement
        for idx, point in enumerate(goal_positions):
            print("Index", idx)
            # Gather original scene arguments
            with open(dir+file, 'r') as f:
                scene_args = json.loads(f.read())
            # Shift the goal position
            if negative:
                x = point[0] + 200 * random.choice([1,-1])
                point = [x,point[1]]
                mutated_scene_args = shift_goal(scene_args,point)
            else:
                mutated_scene_args = shift_goal(scene_args,point)
            mutated_scene_args = add_containers(mutated_scene_args, bbs)
            mutated_scene_args['name'] = f"{file.split('.')[0]}_goalpos_{idx}"
            # Run the scene
            if negative:
                name = f"{savedir}{file.split('.')[0]}"
                name += "_goalpos_{idx}_negative.json"
            else:
                name = f"{savedir}{file.split('.')[0]}_goalpos_{idx}.json"
            with open(name, 'w') as f:
                json.dump(mutated_scene_args, f)  


def sample_scenes(n=1,k=1,criteria_func=None,dir=None):
    """Sample a distribution of n Scenes.

    Args:
        `n: Number of scenes to sample.
        `k: Number of samples to draw from a math.single scene (noisy newtons).
        `criteria_func: Satisfaction criterion for scene samples.
        `dir: Path to which scenes are saved.
    """
    num_containers = 5
    if criteria_func:
        criteria = criteria_func()
    # Sample n scenes via scene argument sets
    ball_args = generate_ball_args(n)
    goal_args = generate_goal_args(n)
    container_args = generate_container_args(
        n,num_containers,ball_args,goal_args)
    # Run the n scenes
    for i in range(n):
        # Add stochasticity
        for j in range(k):
            # Inject Gaussian noise to Ball's position
            noisy_ball_args = list(ball_args[i]*normal(1,0.02,2))

            # Scene components
            objects = [Ball(noisy_ball_args), Goal(goal_args[i]), PlinkoBorder(), BottomBorder()]
            for j in range(num_containers):
                objects.append(Container(*container_args[i][j]))
            # Scene
            scene = Scene(objects)
            scene.instantiate_scene()
            scene.run()
        # Check if Scene passes check
        if criteria_func:
            next(criteria)
            criteria_met = criteria.send(scene)
            if criteria_met:
                n = 0
            else:
                n+=1
        # If saving, save to JSON 
        if dir:
            o_args = {
                'ball_args':(float(ball_args[i][0]),float(ball_args[i][1])),
                'goal_args':(float(goal_args[i][0]),float(goal_args[i][1])),
                'container_args':container_args[i]
            }
            save_scene(dir,f'scene_{i}', scene, o_args)


def check_criteria(scene, conditions=None):
    """Checks criteria for bin membership are met while generating stimuli.

    Args:
        conditions: Dictionary containing user-specified values
                       that are used to generate stimuli.
    """
    def bin_membership(scene,runtime,collision):
        """Convenience function for checking bin membership (cleaner this way)
        mmm a e s t h e t i c s
        
        Args:
            scene: Scene to be binned
            runtime: Runtime bin range
            collision: Collision bin value (yes collision / no collision)
        """
        # Establish runtime membership
        if all(list(map(lambda x: x in range(*runtime), scene.tick_samples))):
            pass
        else:
            return False
        if collision:
            if scene.collision_prob > 0.9:
                return True
            else:
                return False
        else:
            if scene.collision_prob < 0.1:
                return True
            else:
                return False
    runtimes = {'low':(0,151),'med':(151,301),'high':(301,451)}
    if conditions:
        if conditions['sp'] == False:
            if scene.container_collision_prob <  0.9:
                return 'None'
        if conditions['sp'] == True:
            if scene.container_collision_prob >  0.1:
                return 'None'
    if bin_membership(scene,runtimes['low'],True):
        return 'low_yes'
    elif bin_membership(scene,runtimes['low'],False):
        return 'low_no'
    elif bin_membership(scene,runtimes['med'],True):
        return 'med_yes'
    elif bin_membership(scene,runtimes['med'],False):
        return 'med_no'
    elif bin_membership(scene,runtimes['high'],True):
        return 'high_yes'
    elif bin_membership(scene,runtimes['high'],False):
        return 'high_no'
    else:
        return None


def sample_object_arguments(n=1,conditions=None):
    num_containers = 5
    # Sample n scenes via scene argument sets
    ball_args = generate_ball_args(n, conditions)
    if conditions:
        conditions['ball_x'] = [pos[0] for pos in ball_args]
        goal_args = generate_goal_args(n, conditions)
    else:
        goal_args = generate_goal_args(n, conditions)
    container_args = generate_container_args(n,num_containers,ball_args,goal_args)
    return [ball_args,goal_args,container_args]


def sample_scenes_pilot3(dir,conditions=None,n=1,k=1):
    """Sample scenes for Pilot 3.

    Args:
        dir: Directory where accepted scenes will be saved.
        conditions: User-specified conditions for binning the scenes.
        n: Number of counterfactual samples to draw from individual scenes
              (used to compute probabily distributions over scene properties).
        k: How many scenes needed per bin.
    """
    # Number of scenes per condition
    num_per_bin = k
    if conditions:
        bins = conditions['bins']
    else:
        bins = {
            'low_no':0,
            'low_yes':0,
            'med_no':0,
            'med_yes':0,
            'high_no':0,
            'high_yes':0
        }
    while not all(list(map(lambda x: x==num_per_bin, bins.values()))):
        # Generate scene arguments
        ball_args,goal_args,container_args = sample_object_arguments(
            1,conditions)
        # Collision probability
        collision_prob = 0
        container_collision_prob = 0
        tick_samples = []
        # Perturb those arguments N times
        for i in range(n):
            noisy_ball_args = list(*ball_args*normal(1,0.02,2))
            objects = [
                Ball(noisy_ball_args),
                Goal(*goal_args),
                PlinkoBorder(),
                BottomBorder()]
            for j in range(len(container_args[0])):
                objects.append(Container(*container_args[0][j]))
            # Scene
            scene = Scene(objects)
            scene.instantiate_scene()
            scene.run(view=False)
            tick_samples.append(scene.physics.tick)
            # Read out statistics
            collision_prob += scene.physics.handlers['ball_goal'].data['colliding']
            container_collision_prob += scene.physics.handlers['ball_container'].data['colliding']
        # Read out statistics
        scene.tick_samples = tick_samples
        collision_prob /= n
        scene.collision_prob = collision_prob
        container_collision_prob /= n
        scene.container_collision_prob = container_collision_prob
        # Check if statistics meet criteria
        bin_id = check_criteria(scene,conditions)
        # Save pasmath.sing scenes
        if bin_id in bins.keys() and bins[bin_id] < num_per_bin: 
            print(f"Assigned bin: {bin_id}")
            print(f"RT Avg, std, range: {np.mean(scene.tick_samples),np.std(scene.tick_samples),min(scene.tick_samples),max(scene.tick_samples)}")
            print(f"CP: {scene.collision_prob}")
            print(f"CCP: {scene.container_collision_prob}")
            bins[bin_id] += 1
            o_args = {
                'ball_args':(float(ball_args[0][0]),float(ball_args[0][1])),
                'goal_args':(float(goal_args[0][0]),float(goal_args[0][1])),
                'container_args':container_args[0]
            }
            sp = 'yes' if conditions['sp'] else 'no'
            rt = conditions['rt']
            col = 'yes' if conditions['bgc'] else 'no'
            save_scene(
                dir,f'{rt}_{col}col_{sp}sp_{bins[bin_id]}', scene, o_args)


def main():
    pass


if __name__ == "__main__":
    main()
