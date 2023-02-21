import argparse
import os
import json, subprocess

# List of tuples
def ranges(start, stop, offset):
    '''
    Returns a list of P tuples that represent contiguous
    partitions on the number line between Start and Stop
    inclusive, with each partition having size O

    :param start: The start value of number line
    :param stop: The stop value of number line
    :param offset: Size of partitions
    '''
    # Partitions to return
    partitions = []
    # List of ranges
    rs = list(range(start, stop, offset))
    # Build range boundaries
    for r in rs:
        partitions.append((r, r+offset))
    return partitions

def main():
    parser = argparse.ArgumentParser(
        description="Automatically submit jobs using a json file")
    parser.add_argument('jobscript',help="job script to use")
    args = parser.parse_args()

    # Range for parameter N -- (100,151), ..., (450,501)
    d_ranges = ranges(1,1000,50)
    # Range for parameter D -- (5,11), ..., (40,46)
    n_ranges = ranges(1,200,20)

    # Submit a job per parameter setting
    for param_setting in ((n,d) for n in n_ranges for d in d_ranges):
        # N and d parameter ranges
        n, d = param_setting
        n1, n2 = n[0],n[1]
        d1, d2 = d[0],d[1]

        # Get the filename for storage
        fname = f"grid_fits_n{n1}_{n2}_d{d1}_{d2}"
        # The sbatch command
        submit_command = (
            "sbatch " + # sbatch command
            # Job name
            f"--job-name={fname} " +
            # Export relevant variables to jobscript
            f"--export=NRANGE1={n1},NRANGE2={n2}, \
                DRANGE1={d1},DRANGE2={d2},FNAME={fname} " +
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