import pandas as pd
import pymc3 as pm
import numpy as np
import os
import sys
import json
import theano.tensor as tt
import arviz as az
from models import abstraction_simulation_pp

def my_model(theta,x):
    '''
    :param theta: Expected theta == [N, D, E]
    :param x: Expected list of scene arguments
    '''
    # Unpack model params
    N,D,E = theta
    # Model predictions
    y_pred = []
    # Get model predictins for each scene
    for scene in x:
        y_pred.append(abstraction_simulation_pp(scene_args[scene],int(N),D,E))
    # Convert to array
    y_pred = np.array(y_pred)
    return y_pred

# The loglikelihood function
def log_likelihood(theta, x, data, sigma):
    '''
    Normal log-likelihoood
    
    :param data: Empirical repsonse times
    :param sigma: Empirical response time stddev
    :param x: Scene arguments, expected: [scene_1,scene2,...]
    :param theta: Model parameters, expected: [N,D,E]
    '''
    
    # Model simulation times
    y_pred = my_model(theta,x)
    
    # Divergence from data
    retval = -(0.5 / sigma ** 2) * np.sum((data - y_pred) ** 2)
    return retval

# define a theano Op for our likelihood function
class LogLike(tt.Op):
    itypes = [tt.dvector]  # expects a vector of parameter values when called
    otypes = [tt.dscalar]  # outputs a single scalar value (the log likelihood)

    def __init__(self, loglike, data, x, sigma):
        # add inputs as class attributes
        self.likelihood = loglike
        self.data = data
        self.x = x
        self.sigma = sigma

    def perform(self, node, inputs, outputs):
        # the method that is used when calling the Op
        (theta,) = inputs  # this will contain my variables

        # call the log-likelihood function
        logl = self.likelihood(theta, self.x, self.data, self.sigma)

        outputs[0][0] = np.array(logl)  # output the log-likelihood

data = pd.read_json('../data/cleaned_data.json')
scenedir = "../data/scenes/"
scene_files = [s_json for s_json in os.listdir(scenedir) if s_json.endswith('.json')]

scene_args = {}
for file in scene_files:
    with open(scenedir+file, 'r') as f:
        sargs = (json.loads(f.read()))
        scene_args[sargs['name'].split(".")[0]] = sargs

# Observed RT
RT_y_mean = data.groupby('scene').rt.apply(np.mean)
RT_y_std = data.groupby('scene').rt.apply(np.std).mean()
RT_x = RT_y_mean.index.to_list()

abstraction_model = pm.Model()
loglike = LogLike(log_likelihood,RT_y_mean,RT_x,RT_y_std)

with abstraction_model:
    # Priors on model parameters
    # Number of samples to take from simulator
    N = pm.DiscreteUniform("N",lower=1,upper=25)
    # Length of path projection
    D = pm.TruncatedNormal("D",sigma=10, lower=20)
    # Cosine similarity threshold
    E = pm.TruncatedNormal("E",sigma=0.1,lower=0,upper=1)
    
    theta = tt.as_tensor_variable([N,D,E])
    
    pm.Potential("likelihood",loglike(theta))
    
ndraws = 3000  # number of draws from the distribution
nburn = 1000  # number of "burn-in points" (which we'll discard)

with abstraction_model:
    trace = pm.sample(ndraws,tune=nburn, 
                      cores=4,
                      discard_tuned_samples=True, 
                      step=pm.Metropolis(),
                      start = {
                          'N': 10,
                          'D': 100.0,
                          'E': 0.9
                      })
    print(pm.summary(trace).to_string())

with abstraction_model:
  df = pm.trace_to_dataframe(trace)

df.to_json("../data/abstraction_model_pp_fit_1.json")