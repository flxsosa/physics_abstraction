import argparse
import os
import json, subprocess

def main():
    parser = argparse.ArgumentParser(
        description="Automatically submit jobs using a json file")
    parser.add_argument('jobscript',help="job script to use")
    args = parser.parse_args()

    # Range for parameter N -- (100,151), ..., (450,501)
    d_ranges = [(n*50, (n+1)*50+1) for n in range(2,10)]
    # Range for parameter D -- (5,11), ..., (40,46)
    n_ranges = [(n*5, (n+1)*5+1) for n in range(1,9)]
    
    # Submit a job per parameter setting
    for param_setting in ((n,d) for n in n_ranges for d in d_ranges):
        # N and d parameter ranges
        n, d = param_setting
        # Get the filename for storage
        fname = f"grid_fits_n{n[0]}_{n[1]}_d{d[0]}_{d[1]}"
        # The sbatch command
        submit_command = (
            "sbatch " + # sbatch command
            # Job name
            f"--job-name={fname} " +
            # Export relevant variables to jobscript
            f"--export=NRANGE={str(n)},DRANGE={str(d)},FNAME={fname} " +
            # The job script
            args.jobscript)
        # Execute sbatch command
        exit_status = subprocess.call(submit_command,shell=True)
        # Check to make sure job submitted
        if exit_status is 1:
            print("Job {0} failed to submit".format(submit_command))

    print("Done submitting them jobz")

if __name__ == "__main__":
    main()