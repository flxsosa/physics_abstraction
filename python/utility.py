import numpy as np
import cv2
import glob
from objects import *
from simulation import *
from numpy.random import normal
from helper import vid_from_img
from stimuli import generate_ball_args, generate_goal_args, generate_container_args
import json
import os

def add_containers(dir,ddir):
    json_files = [jsonf for jsonf in os.listdir(dir) if jsonf.endswith('.json')]

    for file in json_files:
        obj_map = {
            "Ball":Ball,
            "Container":Container,
            "Goal":Goal,
            "PlinkoBorder":PlinkoBorder,
            "BottomBorder":BottomBorder,
            "Line":Line
        }
        objects = []
        with open(dir+file, 'r') as f:
            scene_args = json.loads(f.read())
            for obj in scene_args['objects']:
                if obj == "Ball":
                    objects.append(obj_map[obj](*scene_args["ball_args"]))
                elif obj == "Goal":
                    objects.append(obj_map[obj](*scene_args["goal_args"]))
                elif obj == "Container":
                    for i in range(len(scene_args["container_args"])):
                        objects.append(obj_map[obj](*scene_args["container_args"][i]))
                elif obj == "Line":
                    for i in range(len(scene_args["line_args"])):
                        objects.append(obj_map[obj](*scene_args["line_args"][i]))
                elif obj == "PlinkoBorder":
                    objects.append(obj_map[obj]())
                elif obj == "BottomBorder":
                    objects.append(obj_map[obj]())
                else:
                    raise ValueError(f"Received an invalid value in load_objects: obj=={obj}")
        container_args = generate_container_args(1,5,scene_args['ball_args'],
                                                scene_args['goal_args'],
                                                scene_args['line_args'])
        for j in range(len(container_args[0])):
            objects.append(Container(*container_args[0][j]))
        sname = file.split('.')[0]
        physics = Physics()
        graphics = Graphics()
        scene = Scene(physics, objects, graphics)
        scene.graphics.instantiate_screen_recorder(ddir,sname)
        scene.instantiate_scene()
        scene.run()
        vid_from_img(sname,ddir)

def scene_json_to_video(odir,ddir,subroutine=None):
    '''
    Converts all of the scene json files into videos.

    :param odir: The directory with the JSONs
    :param dir: The directory to save the videos to
    '''
    json_files = [jsonf for jsonf in os.listdir(odir) if jsonf.endswith('.json')]

    for file in json_files:
        sname = file.split('.')[0]
        print(sname)
        scene = load_scene(odir+file)
        scene.graphics.instantiate_screen_recorder(ddir,sname)
        # scene.graphics.draw_params['ball_alpha'] = True
        scene.instantiate_scene()
        # scene.run(view=True,\
        #     subroutine=subroutine,
        #     name=sname)
        scene.run_path(view=True)
        vid_from_img(sname,ddir)

def scene_json_to_snapshot(odir,ddir):
    '''
    Runs a Scene from a json file until the Scene
    stops via abstraction. Takes a snapshot of the last tick in the Scene.
    Used for debugging the abstraction model.

    :param odir: The directory with the JSONs
    :param dir: The directory to save the snapshots to
    '''
    json_files = [jsonf for jsonf in os.listdir(odir) if jsonf.endswith('.json')]

    for file in json_files:
        sname = file.split('.')[0]
        physics = Physics()
        graphics = Graphics()
        objects = load_objects(odir+file)
        scene = Scene(physics, objects, graphics)
        scene.graphics.framework.display.set_caption(file)
        scene.graphics.initialize_graphics()
        scene.instantiate_scene()
        scene.run(view=True,\
            subroutine=straight_path_collision,
            name=sname)

def save_scene(dir, name, scene, o_args):
    '''
    Record arguments for a Scene and end state of the Scene into
    a JSON.

    :param dir: Path to save to.
    :param name: Name for scene (Filename).
    :param scene: Scene to be saved.
    :param o_args: Object argument dictionary.
    '''
    record = {}
    record['name'] = name
    # record['collision_prob'] = scene.listeners['collision_prob']
    record['screen_size'] = scene.graphics.screen_size
    record['tick'] = scene.physics.tick
    record['tick_samples'] = scene.tick_samples
    record['objects'] = [obj.name for obj in scene.objects]
    for key in o_args.keys():
        record[key] = o_args[key]
    with open(dir+name+'.json', 'w') as f:
        json.dump(record, f)

def fix_json(dir):
    json_files = [jsonf for jsonf in os.listdir(dir) if jsonf.endswith('.json')]

    for file in json_files:
        with open(dir+file, 'r') as f:
            scene_args = json.loads(f.read())
            if type(scene_args['ball_args'][0]) is not list:
                scene_args['ball_args'] = [scene_args['ball_args']]
            if type(scene_args['goal_args'][0]) is not list:
                scene_args['goal_args'] = [scene_args['goal_args']]            
            with open(dir+file, 'w') as f:
                json.dump(scene_args,f)

def load_objects_from_args(args):
    '''
    Load objects from given JSON arguments for a Scene.

    :param args: Path to scene.
    '''
    obj_map = {
        "Ball":Ball,
        "Container":Container,
        "Goal":Goal,
        "PlinkoBorder":PlinkoBorder,
        "BottomBorder":BottomBorder,
        "Line":Line
    }
    objects = []
    scene_args = args
    for obj in scene_args['objects']:
        if obj == "Ball":
            objects.append(obj_map[obj](*scene_args["ball_args"]))
        elif obj == "Goal":
            objects.append(obj_map[obj](*scene_args["goal_args"]))
        elif obj == "Container":
            for i in range(len(scene_args["container_args"])):
                objects.append(obj_map[obj](*scene_args["container_args"][i]))
        elif obj == "Line":
            for i in range(len(scene_args["line_args"])):
                objects.append(obj_map[obj](*scene_args["line_args"][i]))
        elif obj == "PlinkoBorder":
            objects.append(obj_map[obj]())
        elif obj == "BottomBorder":
            objects.append(obj_map[obj]())
        else:
            raise ValueError(f"Received an invalid value in load_objects: obj=={obj}")
    return objects

def load_objects(dir):
    '''
    Load objects from saved JSON arguments for a Scene.

    :param dir: Path to scene.
    '''
    obj_map = {
        "Ball":Ball,
        "Container":Container,
        "Goal":Goal,
        "PlinkoBorder":PlinkoBorder,
        "BottomBorder":BottomBorder,
        "Line":Line
    }
    objects = []
    with open(dir, 'r') as f:
        scene_args = json.loads(f.read())
        for obj in scene_args['objects']:
            if obj == "Ball":
                objects.append(obj_map[obj](*scene_args["ball_args"]))
            elif obj == "Goal":
                objects.append(obj_map[obj](*scene_args["goal_args"]))
            elif obj == "Container":
                for i in range(len(scene_args["container_args"])):
                    objects.append(obj_map[obj](*scene_args["container_args"][i]))
            elif obj == "Line":
                for i in range(len(scene_args["line_args"])):
                    objects.append(obj_map[obj](*scene_args["line_args"][i]))
            elif obj == "PlinkoBorder":
                objects.append(obj_map[obj]())
            elif obj == "BottomBorder":
                objects.append(obj_map[obj]())
            else:
                raise ValueError(f"Received an invalid value in load_objects: obj=={obj}")
    return objects

def load_scene_from_args(args):
    '''
    Load a Scene from given JSON arguments.

    :param args: Path to scene.
    '''
    physics = Physics()
    graphics = Graphics()
    objects = load_objects_from_args(args)

    scene = Scene(physics, objects, graphics)
    scene.graphics.framework.display.set_caption(args['name'])
    return scene

def load_scene(dir):
    '''
    Load a Scene from saved JSON arguments.

    :param dir: Path to scene.
    '''
    physics = Physics()
    graphics = Graphics()
    objects = load_objects(dir)

    scene = Scene(physics, objects, graphics)
    scene.graphics.framework.display.set_caption(dir.split('/')[-1])
    return scene

def view_scenes_in_dir(dir):
    '''
    Convenience function for viewing all of the Scenes 
    saved into one trajectory (for sanity checking)
    
    :param dir: Directory where Scenes are saved.
    '''
    json_files = [jsonf for jsonf in os.listdir(dir) if jsonf.endswith('.json')]

    for file in json_files:
        scene = load_scene(dir+file)
        scene.instantiate_scene()
        scene.run()
        print(f"{file}: {scene.physics.tick}")

def sample_scenes(n=1,k=1,criteria_func=None,dir=None):
    '''
    Sample a distribution of n Scenes.

    :param n: Number of scenes to sample.
    :param k: Number of samples to draw from a single scene (noisy newtons).
    :param criteria_func: Satisfaction criterion for scene samples.
    :param dir: Path to which scenes are saved.
    '''
    num_containers = 5
    if criteria_func:
        criteria = criteria_func()
    # Sample n scenes via scene argument sets
    ball_args = generate_ball_args(n)
    goal_args = generate_goal_args(n)
    container_args = generate_container_args(n,num_containers,ball_args,goal_args)

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
            physics = Physics()
            graphics = Graphics()

            # Scene
            scene = Scene(physics, objects, graphics)
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
    '''
    Checks whether my specific criteria for bin membership are 
    met while generating stimuli.

    :param conditions: Dictionary containing user-specified values
                       that are used to generate stimuli.
    '''
    def bin_membership(scene,runtime,collision):
        '''
        Convenience function for checking bin membership (cleaner this way)
        mmm a e s t h e t i c s
        
        :param scene: Scene to be binned
        :param runtime: Runtime bin range
        :param collision: Collision bin value (yes collision / no collision)
        '''
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
    '''
    Sample scenes for Pilot 3.

    :param dir: Directory where accepted scenes will be saved.
    :param conditions: User-specified conditions for binning the scenes.
    :param n: Number of counterfactual samples to draw from individual scenes
              (used to compute probabily distributions over scene properties).
    :param k: How many scenes needed per bin.
    '''
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
        ball_args,goal_args,container_args = sample_object_arguments(1,conditions)
        # Collision probability
        collision_prob = 0
        container_collision_prob = 0
        tick_samples = []
        # Perturb those arguments N times
        for i in range(n):
            noisy_ball_args = list(*ball_args*normal(1,0.02,2))
            objects = [Ball(noisy_ball_args), Goal(*goal_args), PlinkoBorder(), BottomBorder()]
            for j in range(len(container_args[0])):
                objects.append(Container(*container_args[0][j]))
            physics = Physics()
            graphics = Graphics()

            # Scene
            scene = Scene(physics, objects, graphics)
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
        # print(f"RT ÷Avg, std, range: {np.mean(scene.tick_samples),np.std(scene.tick_samples),min(scene.tick_samples),max(scene.tick_samples)}")
        # Save passing scenes
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
            save_scene(dir,f'{rt}_{col}col_{sp}sp_{bins[bin_id]}', scene, o_args)

def vid_from_img(scene_name,dir,filetype="*.jpg"):
    '''
    Takes images generated from make_video and stitches them into a video
    [DEPRECATED]
    :param scene_name: Name of the simulation for file naming
    :param filetype: Glob parameter
    :param dir: Location to save video to
    '''
    print(f"Passed movie directory: {dir}")
    print(f"Passed movie Scene Name: {scene_name}")
    img_dic = {}
    img_str = []
    size = 0,0
    for filename in glob.glob(dir+filetype):
        img = cv2.imread(filename)
        h,w,l =img.shape
        size = (img.shape[1],img.shape[0])
        img_str.append(filename)
        img_dic[filename] = img
    out = cv2.VideoWriter(dir+scene_name+'.mp4', cv2.VideoWriter_fourcc(*'avc1'),60,size)
    img_str.sort()
    for i in img_str:
        out.write(img_dic[i])
    out.release()
    os.system("rm "+ dir +"*.jpg")