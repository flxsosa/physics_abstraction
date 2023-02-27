from logging import warning
from objects import *
from scene import Scene
from physics import Physics
from graphics import Graphics
#from helper import vid_from_img
from stimuli import generate_container_args
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
#        vid_from_img(sname,ddir)

def scene_json_to_video(odir,ddir,subroutine=None):
    '''
    Converts all of the scene json files into videos.

    :param odir: The directory with the JSONs
    :param dir: The directory to save the videos to
    '''
    json_files = [jsonf for jsonf in os.listdir(odir) if jsonf.endswith('.json')]

    for file in json_files:
        sname = file.split('.')[0]
        scene = load_scene(odir+file)
        scene.graphics.instantiate_screen_recorder(ddir,sname)
        # scene.graphics.draw_params['ball_alpha'] = True
        scene.instantiate_scene()
        # scene.run(view=True,\
        #     subroutine=subroutine,
        #     name=sname)
        scene.run_path(view=True)
#        vid_from_img(sname,ddir)

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

def load_objects_from_args(args,region_test=False):
    '''
    Load objects from given JSON arguments for a Scene.

    :param args: Path to scene.
    '''
    if region_test:
        obj_map = {
            "Ball":Ball,
            "Container":Container,
            "Goal":Region,
            "PlinkoBorder":PlinkoBorder,
            "BottomBorder":BottomBorder,
            "Line":Line
        }
    else:
        obj_map = {
            "Ball":Ball,
            "Container":Container,
            "Goal":Goal,
            "PlinkoBorder":PlinkoBorder,
            "BottomBorder":BottomBorder,
            "Line":Line
        }
    objects = []
    region = None
    scene_args = args
    for obj in scene_args['objects']:
        if obj == "Ball":
            objects.append(obj_map[obj](*scene_args["ball_args"]))
        elif obj == "Goal":
            if "goal_args" not in scene_args.keys():
                warning("Goal object specified in objects but no arguments found.")
                continue
            region = obj_map[obj](*scene_args["goal_args"])
        elif obj == "Container":
            for i in range(len(scene_args["container_args"])):
                objects.append(obj_map[obj](*scene_args["container_args"][i]))
        elif obj == "Line":
            for i in range(len(scene_args["line_args"])):
                objects.append(obj_map[obj](*scene_args["line_args"][i]))
        elif obj == "PlinkoBorder":
            if "plinko_border_args" in scene_args:
                objects.append(obj_map[obj](*scene_args["plinko_border_args"]))
            else:
                objects.append(obj_map[obj]())
        elif obj == "BottomBorder":
            if "bottom_border_args" in scene_args:
                objects.append(obj_map[obj](*scene_args["bottom_border_args"]))
            else:
                objects.append(obj_map[obj]())
        else:
            raise ValueError(f"Received an invalid value in load_objects: obj=={obj}")
    if region != None:
        objects.append(region)
    return objects

def load_objects(dir,region_test=False):
    '''
    Load objects from saved JSON arguments for a Scene.

    :param dir: Path to scene.
    '''
    if region_test:
        obj_map = {
            "Ball":Ball,
            "Container":Container,
            "Goal":Region,
            "PlinkoBorder":PlinkoBorder,
            "BottomBorder":BottomBorder,
            "Line":Line
        }
    else:
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
                if "plinko_border_args" in scene_args:
                    objects.append(LeftBorder(*scene_args["plinko_border_args"]))
                    objects.append(RightBorder(*scene_args["plinko_border_args"]))
                else:
                    objects.append(obj_map[obj]())
            elif obj == "BottomBorder":
                if "bottom_border_args" in scene_args:
                    objects.append(obj_map[obj](*scene_args["bottom_border_args"]))
                else:
                    objects.append(obj_map[obj]())
            else:
                raise ValueError(f"Received an invalid value in load_objects: obj=={obj}")
    return objects

def load_scene_from_args(args,region_test=False):
    '''
    Load a Scene from given JSON arguments.

    :param args: Scene argument.
    '''
    screen_args = args['screen_size']
    physics = Physics()
    graphics = Graphics(*screen_args)
    objects = load_objects_from_args(args,region_test)

    scene = Scene(physics, objects, graphics)
    scene.graphics.framework.display.set_caption(args['name'])
    return scene

def load_scene(dir,region_test=False):
    '''
    Load a Scene from saved JSON arguments.

    :param dir: Path to scene.
    '''
    with open(dir, 'r') as f:
        scene_args = json.loads(f.read())
        screen_args = scene_args['screen_size']
    physics = Physics()
    graphics = Graphics(*screen_args)
    objects = load_objects(dir,region_test=region_test)

    scene = Scene(physics, objects, graphics, dir)
    scene.graphics.framework.display.set_caption(dir.split('/')[-1])
    return scene

def convert_to_ordered_collision_trace(trace,mapping):
    if len(trace) == 0:
        return trace
    ordered_trace = []
    original_trace = trace[0]
    ball,container = original_trace
    ordered_trace.append(mapping[container])
    return ordered_trace

def load_object_arg_pairs(scene_args):
    '''
    Instantiates objects via (object, argument) tuples

    :param scene_args: Arguments for scenes
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
    object_args = []
    for obj in scene_args['objects']:
        if obj == "Ball":
            objects.append(obj_map[obj])
            object_args.append(scene_args["ball_args"])
        elif obj == "Goal":
            objects.append(obj_map[obj])
            object_args.append(scene_args["goal_args"])
        elif obj == "Container":
            for i in range(len(scene_args["container_args"])):
                objects.append(obj_map[obj])
                object_args.append(scene_args["container_args"][i])
        elif obj == "Line":
            for i in range(len(scene_args["line_args"])):
                objects.append(obj_map[obj])
                object_args.append(scene_args["line_args"][i])
        elif obj == "PlinkoBorder":
            objects.append(obj_map[obj])
            if "plinko_border_args" in scene_args:
                object_args.append(scene_args["plinko_border_args"])
            else:
                object_args.append(obj_map[obj]())
        elif obj == "BottomBorder":
            objects.append(obj_map[obj])
            if "bottom_border_args" in scene_args:
                object_args.append(scene_args["bottom_border_args"])
            else:
                object_args.append(obj_map[obj]())
        else:
            raise ValueError(f"Received an invalid value in load_objects: obj=={obj}")
    return objects, object_args
