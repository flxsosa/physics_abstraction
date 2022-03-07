import argparse
import pandas as pd
import pymc3 as pm
import numpy as np
import arviz as az
import os
import json
import theano.tensor as tt
from models import abstraction_simulation_pp as sim

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

def main():
    parser = argparse.ArgumentParser(
        description="Automatically submit jobs using a json file")
    parser.add_argument('datadir', 
        help="read-directory where participant data is")
    parser.add_argument('scenedir',
        help='read-directory where scene simulation parameter files are')
    parser.add_argument('savedir',
        help='write-directory where model parameter files saved to')
    parser.add_argument('numsamples', default=1,
        help='number of samples to draw per chain')
    parser.add_argument('burnin', default=1,
        help='number of samples for burn-in')
    args = parser.parse_args()
    
    def my_model(theta,x):
        '''
        :param theta: List of parameter candidates for simulator == [N, D, E]
        :param x: Expected list of inputs for simulator to be evaluated on
        '''
        # Unpack model params
        N,D,E = theta
        # Model predictions
        y_pred = []
        # Get model predictins for each scene
        for x_ in x:
            y_pred.append(
                sim(scene_args[x_], int(N), D, E)[-1][0])
        # Convert to array
        y_pred = np.array(y_pred)
        return y_pred

    def log_likelihood(theta, x, data, sigma):
        '''
        Gaussian divergence

        :param data: Empirical data to fit to (response times)
        :param sigma: Empirical data std dev
        :param x: Input arguments for simulator (Scene arguments, expected: [scene_1,scene2,...])
        :param theta: Model parameters == [N,D,E]
        '''
        
        # Model outputs, given candidate parameter values
        y_pred = my_model(theta,x)
        all_equal = list(map(lambda x,y: x == y, data.index,x))
        print(f"Data minus predictions: {np.sum(data-y_pred)}")
        # Divergence from input data
        return -(0.5 / sigma ** 2) * np.sum((data - y_pred) ** 2)
    
    # Extract args
    data = pd.read_json(args.datadir)
    scenedir = args.scenedir
    ndraws = int(args.numsamples)  # number of draws from the distribution
    nburn = int(args.burnin)  # number of "burn-in points" (which we'll discard)
    
    # Collect scene parameter files for simulator
    scene_files = [s_json for s_json in os.listdir(scenedir) if s_json.endswith('.json')]
    scene_args = {}
    for file in scene_files:
        with open(scenedir+file, 'r') as f:
            sargs = (json.loads(f.read()))
            scene_args[sargs['name'].split(".")[0]] = sargs

    # Collect observed mean RT from empirical data
    RT_y_mean = data.groupby('scene').rt.apply(np.mean)
    RT_y_std = data.groupby('scene').rt.apply(np.std).mean()
    RT_x = RT_y_mean.index.to_list()

    # Define model
    abstraction_model = pm.Model()
    loglike = LogLike(log_likelihood,RT_y_mean,RT_x,RT_y_std)
    with abstraction_model:
        # Priors on model parameters
        # Number of samples to take from simulator
        N = pm.DiscreteUniform("N",lower=5,upper=25)
        # Length of path projection
        D = pm.TruncatedNormal("D",sigma=1, lower=50)
        # Cosine similarity threshold
        E = pm.TruncatedNormal("E",sigma=0.1,lower=0.7,upper=1)
        # Wrap the params in a theano tensor
        theta = tt.as_tensor_variable([N,D,E])
        # Likelihood distribution
        pm.Potential("likelihood",loglike(theta))

    # Sample the model
    with abstraction_model:
        # Store in trace variable
        trace = pm.sample(ndraws,
                        cores=1,
                        chains=1,
                        tune=nburn,
                        step=pm.Metropolis(),
                        start = {
                            'N': 10,
                            'D': 100.0,
                            'E': 0.9
                        })
        # If possible, print trace summary
        print(pm.summary(trace).to_string())
    
    # Save model to storage
    with abstraction_model:
        df = pm.trace_to_dataframe(trace)
    df.to_json(args.savedir)
    
    # Alert that no errors occurred 
    print(f"All seems to have gone well...")

if __name__ == "__main__":
    main()