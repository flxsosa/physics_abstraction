from simulation import Graphics, Physics, Scene
from utility import load_scene,load_scene_from_args, vid_from_img, view_scenes_in_dir
import models
import json
import numpy as np
import copy
from math import cos, sin, radians, sqrt

def new_scene():
    scene_args = {} 
    scene_args['screen_size'] = [800,2000]
    scene_args['objects'] = ['Ball','Goal','BottomBorder','PlinkoBorder','Container']
    scene_args['bottom_border_args'] = [[10,1380],[790,1380]]
    scene_args['plinko_border_args'] = [1392,800]
    scene_args['name'] = ''
    return scene_args

def build_stimuli_bottom_up_goal_first_enumerative():
    step_size = 10
    # Scene arguments
    scene_args = new_scene()
    # Initial container args
    scene_args['container_args'] = []
    scene_args['container_args'] = add_containers_bottom_up_enumerative(scene_args)
    ball_args = add_ball_args_bottom_up(scene_args)
    scene_args['ball_args'] = ball_args
    # Run the scene forward and get landing position
    scene = load_scene_from_args(scene_args)
    scene.instantiate_scene()
    scene.run(view=False)
    for o in scene.objects:
        if o.name == "Ball":
            x_goal = o.body.position[0]
    y_goal = 1356
    scene_args['goal_args'] = [[x_goal,y_goal]]

    while not scene_criteria_met(scene_args):
        print(f"Containers in scene {len(scene_args['container_args'])}")
        mutated_scene_args = copy.deepcopy(scene_args)
        # Create container
        container_args = add_containers_bottom_up(mutated_scene_args)
        mutated_scene_args['container_args'] = container_args
        # Add ball above newly created container
        ball_args = add_ball_args_bottom_up(mutated_scene_args)
        mutated_scene_args['ball_args'] = ball_args
        # Determine if model criteria are met
        if model_criteria_met(mutated_scene_args):
            print("Met criteria")
            scene_args = copy.deepcopy(mutated_scene_args)
        else:
            print("Did not meet criteria")
    return scene_args

def build_stimuli_bottom_up_goal_first():
    # Scene arguments
    scene_args = new_scene()
    # Initial container args
    scene_args['container_args'] = []
    scene_args['container_args'] = add_containers_bottom_up(scene_args)
    ball_args = add_ball_args_bottom_up(scene_args)
    scene_args['ball_args'] = ball_args
    # Run the scene forward and get landing position
    scene = load_scene_from_args(scene_args)
    scene.instantiate_scene()
    scene.run(view=False)
    for o in scene.objects:
        if o.name == "Ball":
            x_goal = o.body.position[0]
    y_goal = 1356
    scene_args['goal_args'] = [[x_goal,y_goal]]

    while not scene_criteria_met(scene_args):
        print(f"Containers in scene {len(scene_args['container_args'])}")
        mutated_scene_args = copy.deepcopy(scene_args)
        # Create container
        container_args = add_containers_bottom_up(mutated_scene_args)
        mutated_scene_args['container_args'] = container_args
        # Add ball above newly created container
        ball_args = add_ball_args_bottom_up(mutated_scene_args)
        mutated_scene_args['ball_args'] = ball_args
        # Determine if model criteria are met
        if model_criteria_met(mutated_scene_args):
            print("Met criteria")
            scene_args = copy.deepcopy(mutated_scene_args)
        else:
            print("Did not meet criteria")
    return scene_args

def build_stimuli_bottom_up():
    # Scene arguments
    scene_args = new_scene()
    # Sample goal args
    x = np.random.uniform(100,700)
    y = 1356
    scene_args['goal_args'] = [[x,y]]
    # Initial container args
    scene_args['container_args'] = []
    scene_args['ball_args'] = []
    timeout = 100
    count = 0
    # Begin search
    while not scene_criteria_met(scene_args):
        if count >= timeout and len(scene_args['container_args']) == 0:
            count = 0
            x = np.random.uniform(100,700)
            y = 1356
            scene_args['goal_args'] = [[x,y]]
        count += 1
        print(f"Containers in scene {len(scene_args['container_args'])}")
        mutated_scene_args = copy.deepcopy(scene_args)
        # Create container
        container_args = add_containers_bottom_up(mutated_scene_args)
        mutated_scene_args['container_args'] = container_args
        # Add ball above newly created container
        ball_args = add_ball_args_bottom_up(mutated_scene_args)
        mutated_scene_args['ball_args'] = ball_args
        # Determine if model criteria are met
        if model_criteria_met(mutated_scene_args):
            print("Met criteria")
            scene_args = copy.deepcopy(mutated_scene_args)
        else:
            print("Did not meet criteria")
    return scene_args

def scene_criteria_met(scene_args):
    if len(scene_args['container_args']) > 1:
        return True
    for c_arg in scene_args['container_args']:
        if c_arg[1] > 300:
            return True
    return False

def model_criteria_met(scene_args):
    # print("Checking collision probability...")
    # Run both models on scene
    sim_result = models.simulation(scene_args,num_samples=100,noise=0.02)
    abs_result = models.abstraction(scene_args=scene_args,num_samples=100)
    # print(f"Simulation collision prob: {np.mean(sim_result['collision_probability'])}")
    # print(f"Abstraction collision prob: {np.mean(abs_result['collision_probability'])}")
    # Make sure ball collides with goal under both models
    if np.mean(sim_result['collision_probability']) < 0.10:
        return False
    # # Check abstraction model
    if np.mean(abs_result['collision_probability']) < 0.10:
        return False
    # print("Checking collision trace...")
    # Check number of containers
    num_containers = len(scene_args['container_args'])
    expected_collision_trace = list(range(1,num_containers+1))
    # print(f"Expected trace: {expected_collision_trace}")
    # Make sure both models have the same collision trace
    # print("Running simulation model...")
    sim_result = models.simulation(scene_args,num_samples=1,noise=0.0)
    # print("Running abstraction model...")
    abs_result = models.abstraction(scene_args=scene_args,num_samples=1,noise=None)
    # print("Checking collision trace equivlance...")
    return abs_result['collision_trace'] == sim_result['collision_trace'] == expected_collision_trace 

def print_trace(scene_args):
    print("Actual trace")
    # Make sure both models have the same collision trace
    abs_result = models.abstraction(scene_args=scene_args,num_samples=1,noise=None)
    sim_result = models.simulation(scene_args,num_samples=1,noise=0.0)
    print("Simulation trace:")
    for trace in sim_result['collision_trace']:
        print(trace)    
    print("Abstraction trace:")
    for trace in abs_result['collision_trace']:
        print(trace)  

def add_containers_bottom_up_enumerative(scene_args):
    if 'goal_args' in scene_args.keys():
        goal_pos = scene_args['goal_args'][0]
    else:
        goal_pos = [400,0]
    xs = list(range(40,770,10))
    ys = list(range(300,1210,10))
    if len(scene_args['container_args']) == 0:
        new_x = np.random.randint(80,720)
        new_y = np.random.randint(800,1200)
        id = 0
    else:
        # Get last container
        last_container = scene_args['container_args'][-1]
        # Get container position
        last_container_pos = last_container[0]
        last_x = last_container_pos[0]
        last_y = last_container_pos[1]
        # Use this as bounds posiiton for new container
        if last_x > 400:
            new_x = np.random.randint(80,last_x-80)
        else:
            new_x = np.random.randint(last_x + 80, 720)
        new_y = np.random.randint(300,last_y-100)
    # Get length and width of container
    length = np.random.randint(70,100)
    width = 0
    # Get rotation
    if new_x < goal_pos[0]:
        rot = np.random.randint(10,60)
    elif new_x > goal_pos[0]:
        rot = np.random.randint(-60,-10)
    else:
        rot = np.random.randint(-10,10)
    # Get id
    id = len(scene_args['container_args']) + 1
    # Add new container
    container_args = scene_args['container_args']
    container_args.append([[new_x,new_y],length,width,rot,id])
    return container_args

def add_containers_bottom_up(scene_args):
    if 'goal_args' in scene_args.keys():
        goal_pos = scene_args['goal_args'][0]
    else:
        goal_pos = [400,0]
    if len(scene_args['container_args']) == 0:
        new_x = np.random.randint(80,720)
        new_y = np.random.randint(800,1200)
        id = 0
    else:
        # Get last container
        last_container = scene_args['container_args'][-1]
        # Get container position
        last_container_pos = last_container[0]
        last_x = last_container_pos[0]
        last_y = last_container_pos[1]
        # Use this as bounds posiiton for new container
        if last_x > 400:
            new_x = np.random.randint(80,last_x-80)
        else:
            new_x = np.random.randint(last_x + 80, 720)
        new_y = np.random.randint(300,last_y-100)
    # Get length and width of container
    length = np.random.randint(70,100)
    width = 0
    # Get rotation
    if new_x < goal_pos[0]:
        rot = np.random.randint(10,60)
    elif new_x > goal_pos[0]:
        rot = np.random.randint(-60,-10)
    else:
        rot = np.random.randint(-10,10)
    # Get id
    id = len(scene_args['container_args']) + 1
    # Add new container
    container_args = scene_args['container_args']
    container_args.append([[new_x,new_y],length,width,rot,id])
    return container_args

def add_ball_args_bottom_up(scene_args):
    # Get last container
    last_container = scene_args['container_args'][-1]
    # Get container position
    last_container_pos = last_container[0]
    last_x = last_container_pos[0]
    # Return ball above last container
    return [[last_x, 150]]

def make_scene_grid(screen_size,grid_step=100):
    x, y = screen_size
    y -= 800
    offset_x = 100
    offset_y = 300
    # Get pixel values of area
    yi, yf = offset_y, y
    xi,xf = offset_x, x
    ys = list(range(yi,yf+grid_step,100))
    xs = list(range(xi,xf+grid_step,100))
    return xs, ys

def add_container_from_position(container_position, rot):
    x,y = container_position
    length = 0
    width = 70
    return [container_position, width, length, rot]

def build_stimuli_bottom_up_grid():
    # Make new scene
    scene_args = new_scene()
    # Get screen size
    scene_size = scene_args['screen_size']
    # Make a grid
    row_pos, col_pos = make_scene_grid(scene_size)
    col_pos.reverse()
    print(row_pos,col_pos)
    # Place a container in each possible point of the grid
    for i in range(len(row_pos)-1):
        for j in range(len(col_pos)):
            for rot1 in range(-80,90,10):
                container_pos_1 = [row_pos[i], col_pos[j]]
                # Construct scene                
                scene_args['container_args'] = []
                scene_args['container_args'].append(add_container_from_position(container_pos_1,rot1))
                ball_args = add_ball_args_bottom_up(scene_args)
                scene_args['ball_args'] = ball_args
                # print(scene_args['ball_args'])
                # print(scene_args['container_args'])
                # Run the scene forward and get landing position
                scene = load_scene_from_args(scene_args)
                scene.instantiate_scene()
                scene.run(view=False)#,fname="test",record=True)
                for o in scene.objects:
                    if o.name == "Ball":
                        x_goal = o.body.position[0]
                y_goal = 1356
                scene_args['goal_args'] = [[x_goal,y_goal]]
                # scene = load_scene_from_args(scene_args)
                # scene.instantiate_scene()
                # scene.run(view=False)#,fname="test",record=True)
                # print(scene_args['goal_args'])
                # Add second container
                for k in range(i+1,len(row_pos)):
                    for l in range(len(col_pos)):
                        for rot2 in range(-80,90,10):
                            container_pos_2 = [row_pos[k],col_pos[l]]
                            # print(f"Container 1: {container_pos_1} Container 2: {container_pos_2}")
                            # For each point, run the models
                            mutated_scene_args = copy.deepcopy(scene_args)
                            # Create container
                            mutated_scene_args['container_args'].append(add_container_from_position(container_pos_2,rot2))
                            # Add ball above newly created container
                            ball_args = add_ball_args_bottom_up(mutated_scene_args)
                            mutated_scene_args['ball_args'] = ball_args
                            # print(mutated_scene_args['ball_args'])
                            # print(mutated_scene_args['container_args'])
                            # Determine if model criteria are met
                            if model_criteria_met(mutated_scene_args):
                                print("Met criteria")
                                scene = load_scene_from_args(mutated_scene_args)
                                scene.instantiate_scene()
                                scene.run(view=True,fname="test",record=True)
                                scene_args = copy.deepcopy(mutated_scene_args)
                                with open(f"~/Desktop/"+{i,j,k,l}+'.json', 'w') as f:
                                    json.dump(scene_args, f)
                            else:
                                # print("Did not meet criteria")
                                continue
                        # return
        # Return the scenes that meet the criteria
        return

def main():
    build_stimuli_bottom_up_grid()

if __name__ == "__main__":
    main()