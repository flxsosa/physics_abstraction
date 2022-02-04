from objects import *
from simulation import *
from numpy.random import normal
from abstraction import straight_path_collision

def load_object_arg_pairs(scene_args):
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
            object_args.append([])
        elif obj == "BottomBorder":
            objects.append(obj_map[obj])
            object_args.append([])
        else:
            raise ValueError(f"Received an invalid value in load_objects: obj=={obj}")
    return objects, object_args

def determinstic_simulation(scene_args):
    '''
    Deterministic physics simulator. Model outputs are end
    state of the scene and the number of ticks of one run 
    of a scene with no noise.
    '''
    ticks = []
    collision_prob = 0
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
    scene.instantiate_scene()
    scene.run(view=False)
    # Get ticks
    ticks.append(scene.physics.tick)
    # Get collision probability
    collision_prob += scene.physics.handlers['ball_goal'].data['colliding']
    
    return collision_prob, 1, ticks

def stochastic_simulation(scene_args,samples=100,noise=0.02):
    '''
    Stochastic physics simulator. Model outputs are the
    probability ratings for end states and the
    averaged number of ticks over N runs of a scene with 
    S noise.
    '''
    ticks = []
    collision_prob = 0

    for i in range(samples):
        objects = []
        objs,args = load_object_arg_pairs(scene_args)
        for o,a in zip(objs, args):
            if o.__name__ == "Ball":
                noisy_a = list(*a*normal(1,noise,2))
                objects.append(o(noisy_a))
            elif o.__name__ == "PlinkoBorder" or o.__name__ == "BottomBorder":
                objects.append(o())
            else:
                objects.append(o(*a))
        physics = Physics()
        graphics = Graphics()

        # Scene
        scene = Scene(physics, objects, graphics)
        scene.instantiate_scene()
        scene.run(view=False)
        ticks.append(scene.physics.tick)
        # Read out statistics
        collision_prob += scene.physics.handlers['ball_goal'].data['colliding']
    # Read out statistics
    collision_prob /= samples
    
    return collision_prob, samples, ticks

def sprt_closed(scene_args,T=2,samples=100,noise=0.02):
    '''
    Sequential probability ratio test (Hamrick et al, 2015; 
    Wald, 1947). Model outputs are the probability ratings
    for end states and the number of samples needed to decide
    on an end state.
    '''
    ticks = []
    collision_prob = 0
    for i in range(samples):
        objects = []
        objs,args = load_object_arg_pairs(scene_args)
        for o,a in zip(objs, args):
            if o.__name__ == "Ball":
                noisy_a = list(*a*normal(1,noise,2))
                objects.append(o(noisy_a))
            elif o.__name__ == "PlinkoBorder" or o.__name__ == "BottomBorder":
                objects.append(o())
            else:
                objects.append(o(*a))
        physics = Physics()
        graphics = Graphics()

        # Scene
        scene = Scene(physics, objects, graphics)
        scene.instantiate_scene()
        scene.run(view=False)
        ticks.append(scene.physics.tick)
        # Read out statistics
        collision_prob += scene.physics.handlers['ball_goal'].data['colliding']
    # Read out statistics
    collision_prob /= samples
    p = collision_prob
    # Compute probability of choose "yes" collision
    prob_choosing_yes = p**T / (p**T + (1-p)**T)
    # Compute expected samples
    if p == 0.0:
        N = (T/(1-2*p)) - (2*T / (1-2*p))
    elif p == 0.5:
        N = T # This should actually be infinity
    else:
        N = (T/(1-2*p)) - (2*T / (1-2*p)) * ((1-((1-p)/p)**T)/(1-((1-p)/p)**(2*T)))
    return prob_choosing_yes, N, ticks

def sprt(scene_args,noise=0.02,T=2):
    '''
    Sequential probability ratio test (Hamrick et al, 2015; 
    Wald, 1947). Model outputs are the probability ratings
    for end states and the number of samples needed to decide
    on an end state.
    '''
    # Stopping criterion
    yn = 0
    # Num samples
    N = 0
    # Scene args
    ticks = []
    while abs(yn) != T:
        objects = []
        objs,args = load_object_arg_pairs(scene_args)
        for o,a in zip(objs, args):
            if o.__name__ == "Ball":
                noisy_a = list(*a*normal(1,noise,2))
                objects.append(o(noisy_a))
            elif o.__name__ == "PlinkoBorder" or o.__name__ == "BottomBorder":
                objects.append(o())
            else:
                objects.append(o(*a))
        physics = Physics()
        graphics = Graphics()

        # Scene
        scene = Scene(physics, objects, graphics)
        scene.instantiate_scene()
        scene.run(view=False)
        ticks.append(scene.physics.tick)
        # Read out statistics
        yn += 1 if scene.physics.handlers['ball_goal'].data['colliding'] else -1
        N += 1

    # Compute choice
    if yn < 0:
        prob_choosing_yes = 0
    else:
        prob_choosing_yes = 1
    return prob_choosing_yes, N, ticks

def abstraction_simulation_sp(scene_args):
    '''
    Deterministic physics simulator. Model outputs are end
    state of the scene and the number of ticks of one run 
    of a scene with no noise.
    '''
    ticks = []
    collision_prob = 0
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
    scene.instantiate_scene()
    scene.run(view=False,\
        subroutine=straight_path_collision)
    ticks.append(scene.physics.tick)
    # Get collision probability
    collision_prob += scene.physics.handlers['ball_goal'].data['colliding']
    
    return collision_prob, 1, ticks

def abstraction_simulation_pp(scene_args,N=5,D=100,E=0.9):
    '''
    Deterministic physics simulator. Model outputs are end
    state of the scene and the number of ticks of one run 
    of a scene with no noise.
    '''
    ticks = []
    collision_prob = 0
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
    scene.instantiate_scene()
    scene.run_path(view=False,N=N,D=D,E=E)
    ticks.append(scene.physics.tick)
    # Get collision probability
    collision_prob += scene.physics.handlers['ball_goal'].data['colliding']
    
    return collision_prob, 1, ticks
