import argparse
import os
import json, subprocess

dir="~/"

def main():
    parser = argparse.ArgumentParser(
        description="Automatically submit jobs using a json file")
    parser.add_argument('jobscript',help="job script to use")
    parser.add_argument('directory', help="where to store inference results")
    parser.add_argument('parameters',help='json parameter file to use')
    parser.add_argument('-t','--test',action='store_false',help='test scripts without submitting them')
    args = parser.parse_args()

    with open(args.parameters,mode='r') as jsonfiles:
        # Grab parameters from json
        parameters = json.load(jsonfiles)
        chain_p = parameters["chain"] # parameters for chain
        simulator_p = parameters["sampler"] # parameters for simulator
        # Number of chains, number of sampler per chain, burnin per chain
        num_chains, num_samples, burnin = chain_p["numchains"], chain_p["numsamples"], chain_p["burnin"]
        # Go through the jobs
        for chain_idx in range(num_chains):
            # Get the filename for storage
            fname = f"abstraction_fits_{chain_idx}"
            # The sbatch command
            submit_command = (
                "sbatch " + # sbatch command
                # Output log files here
                f"- o ~/projects/physabs/.out/{fname}.job_log " +
                # Job name
                f"--job-name={fname} " +
                f"--export=FNAME={fname} " +
                # The job script!
                args.jobscript)
            # Check if job is a test job
            if not args.test:
                print(submit_command)
            else:
                exit_status = subprocess.call(submit_command,shell=True)
                # Check to make sure job submitted
                if exit_status is 1:
                    print("Job {0} failed to submit".format(submit_command))

    print("Done submitting them jobz")

if __name__ == "__main__":
    main()