import argparse
import subprocess
from __future__ import print_function # Only Python 2.x

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

# Example
for path in execute(["locate", "a"]):
    print(path, end="")

def ranges(start, stop, offset):
    """
    Returns a list of P tuples that represent contiguous
    partitions on the number line between Start and Stop
    inclusive, with each partition having size O

    Args:
        start: The start value of number line
        stop: The stop value of number line
        offset: Size of partitions

    Outputs:
        partitions: A list of ranges.
    """
    # Partitions to return
    partitions = []
    # List of ranges
    rs = list(range(start, stop, offset))
    # Build range boundaries
    for r in rs:
        partitions.append((r, r+offset))
    return partitions


def main():
    """Main entrypoint for job submissions."""
    parser = argparse.ArgumentParser(
        description='Submits multiple jobs per parameter partition.')
    parser.add_argument('jobscript',help="job script to use")
    args = parser.parse_args()
    # Range for parameter N -- (100,151), ..., (450,501)
    d_ranges = ranges(1,1000,100)
    # Range for parameter D -- (5,11), ..., (40,46)
    n_ranges = ranges(1,1000,100)
    # Submit a job per parameter setting
    for param_setting in ((n,d) for n in n_ranges for d in d_ranges):
        # N and d parameter ranges
        n, d = param_setting
        n1, n2 = n[0],n[1]
        d1, d2 = d[0],d[1]
        # Get the filename for storage
        fname = f'grid_fits_n{n1}_{n2}_d{d1}_{d2}'
        # The sbatch command
        submit_command = (
            'sbatch ' +
            # Job name
            f"--job-name={fname} " +
            # Export relevant variables to jobscript
            '--export=' + 
            f'NRANGE1={n1},NRANGE2={n2}' +
            f'DRANGE1={d1},DRANGE2={d2}' +
            # The job script
            args.jobscript)
        # Execute sbatch command
        exit_status = subprocess.call(submit_command, shell=True)
        # Check to make sure job submitted
        if exit_status == 1:
            print(f'Job {submit_command} failed to submit')
    print('Done submitting them jobz')


if __name__ == "__main__":
    main()
