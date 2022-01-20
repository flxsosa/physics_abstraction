def determinstic_simulation(scene):
    '''
    Deterministic physics simulator. Model outputs are end
    state of the scene and the number of ticks of one run 
    of a scene with no noise.
    '''
    scene.forward(view=False)
    # Output will correspond with the number of ticks of scene
    prob_of_choosing_yes = scene.num_collisions
    num_samples = scene._tick
    scene.clear_vals()
    return prob_of_choosing_yes, num_samples

def stochastic_simulation(scene,samples=100,noise=0.05):
    '''
    Stochastic physics simulator. Model outputs are the
    probability ratings for end states and the
    averaged number of ticks over N runs of a scene with 
    S noise.
    '''
    scene.forward_stochastic(view=False,n=samples)
    # Output will correspond with average number of ticks
    prob_of_choosing_yes = scene.num_collisions/samples
    num_samples = scene._tick
    scene.clear_vals()
    return prob_of_choosing_yes, num_samples

def sprt_closed(scene,T=2,samples=100):
    '''
    Sequential probability ratio test (Hamrick et al, 2015; 
    Wald, 1947). Model outputs are the probability ratings
    for end states and the number of samples needed to decide
    on an end state.
    '''
    # Determine distribution of end states
    scene.forward_stochastic(view=False,n=samples)
    # Extract probability of collision
    p = scene.num_collisions/samples
    # Compute probability of choose "yes" collision
    prob_choosing_yes = p**T / (p**T + (1-p)**T)
    # Compute expected samples
    if p == 0.0:
        N = (T/(1-2*p)) - (2*T / (1-2*p))
    elif p == 0.5:
        N = T # This should actually be infinity
    else:
        N = (T/(1-2*p)) - (2*T / (1-2*p)) * ((1-((1-p)/p)**T)/(1-((1-p)/p)**(2*T)))
    scene.clear_vals()
    return prob_choosing_yes, N

def sprt(scene,T=2,samples=100):
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
    while abs(yn) != T:
        scene.forward_stochastic(view=False,n=1)
        yn += 1 if scene.collision else -1
        N += 1

    # Compute choice
    if yn < 0:
        prob_choosing_yes = 0
    else:
        prob_choosing_yes = 1
    N *= scene._tick
    # REset scene for other models
    scene.clear_vals()
    return prob_choosing_yes, N

def abstraction_simulation(scene, samples=1):
    '''
    Deterministic physics simulator. Model outputs are
    end state of the scene and number of ticks of one 
    run of a scene while using abstraction subroutines.
    '''
    scene.use_abstractions = True
    scene.forward(view=False)
    prob_of_choosing_yes = int(scene.abstraction_collision)
    num_samples = scene._tick
    scene.use_abstractions = False
    scene.clear_vals()
    return prob_of_choosing_yes, num_samples
