from objects import *
from simulation import Scene, Physics, Graphics
from numpy.random import normal
from scipy.stats import truncnorm

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

def simulation(scene_args,num_samples=1,noise=0.0,view=False):
    '''
    Stochastic physics simulator. Model outputs are the
    probability ratings for end states and the
    averaged number of ticks over N runs of a scene with 
    S noise.

    :param scene_args: Arguments for scenes
    :param samples: Number of samples to draw
    :param noise: Noise injected into simulator
    '''
    object_id_map = {}
    dist = {
        "collision_probability":[],
        "simulation_time":[],
        'collision_trace':[]
        }
    # Sample trajectories
    for i in range(num_samples):
        # We separate the Ball from everything else so we can
        #   add noise to the ball's starting location
        objects = []
        objs,args = load_object_arg_pairs(scene_args)
        for o,a in zip(objs, args):
            if o.__name__ == "Ball":
                noisy_a = list(*a*normal(1,noise,2))
                objects.append(o(noisy_a))
            else:
                try:
                    objects.append(o(*a))
                except TypeError:
                    objects.append(o())
        physics = Physics()
        graphics = Graphics()

        # Scene
        scene = Scene(physics, objects, graphics)
        for obj in scene.objects:
            object_id_map[id(obj.components[-1])] = obj.id
        scene.instantiate_scene()
        scene.run(view=view)
        # Read out statistics
        dist['collision_probability'].append(int(scene.physics.handlers['ball_goal'].data['colliding']))
        dist['simulation_time'].append(scene.physics.tick)
        dist['collision_trace'].append(convert_to_ordered_collision_trace(scene.physics.handlers['ball_container'].data['collision_trace'],object_id_map))
    
    return dist

def _abstraction(scene_args,N=5,D=100,E=0.8,view=False):
    '''
    Deterministic physics simulator. Model outputs are end
    state of the scene and the number of ticks of one run 
    of a scene with no noise.

    :param scene_args: Arguments for scenes
    :param N: Number of forward passes of physics engine
    :param D: Length of path projection
    :oparam E: Cossim threshold for accepting abstraction
    '''
    object_id_map = {}
    ticks = 0
    collision_prob = 0
    collision_trace = []
    # Run scene
    objects = []
    objs,args = load_object_arg_pairs(scene_args)
    for o,a in zip(objs, args):
        try:
            objects.append(o(*a))
        except TypeError:
            objects.append(o())
    physics = Physics()
    graphics = Graphics()

    # Scene
    scene = Scene(physics, objects, graphics)
    for obj in scene.objects:
        object_id_map[id(obj.components[-1])] = obj.id
    scene.instantiate_scene()
    scene.run_path(view=view,N=N,D=D,E=E)
    ticks += scene.physics.tick
    # Get collision probability
    collision_prob += scene.physics.handlers['ball_goal'].data['colliding']
    collision_trace = convert_to_ordered_collision_trace(scene.physics.handlers['ball_container'].data['collision_trace'],object_id_map)
    return collision_prob, ticks, collision_trace

def abstraction(scene_args,N=5,D=100,E=0.9,num_samples=100,noise=10,view=False):
    '''
    Deterministic physics simulator. Model outputs are end
    state of the scene and the number of ticks of one run 
    of a scene with no noise.

    :param scene_args: Arguments for scenes
    :param N: Number of forward passes of physics engine
    :param D: Length of path projection
    :oparam E: Cossim threshold for accepting abstraction
    '''
    
    def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
        return truncnorm(
            (low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)
    
    if noise == None:
        ns = [N]*num_samples
        ds = [D]*num_samples
        es = [E]*num_samples
    else:
        # Create parameter distributions
        N_rv = get_truncated_normal(mean=N,sd=N/noise, low=1, upp=1000)
        ns = N_rv.rvs(num_samples)
        D_rv = get_truncated_normal(mean=D,sd=D/noise, low=1, upp=1000)
        ds = D_rv.rvs(num_samples)
        E_rv = get_truncated_normal(mean=E,sd=E/noise, low=0, upp=1)
        es = E_rv.rvs(num_samples)
    # Set up model output dictionary
    dist = {
        "collision_probability":[],
        "simulation_time":[],
        "collision_trace":[]
        }
    # Collect num_samples samples from model
    for i in range(num_samples):
        n,d,e = ns[i], ds[i], es[i]
        coll_prob, sim_time, coll_trace = _abstraction(scene_args,N=n,D=d,E=e)
        dist['collision_probability'].append(coll_prob)
        dist['simulation_time'].append(sim_time)
        dist['collision_trace'].append(coll_trace)

    return dist 