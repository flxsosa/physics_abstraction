import pandas as pd
import glob
import argparse

def main_cluster():
    '''
    Combines csv files of model outputs computed on cluster.
    Ignores headers are removes duplicate rows.
    '''
    parser = argparse.ArgumentParser(
            description="Combine all CSVs in a diretory into one CSV")
    parser.add_argument('datadir',help="Where the data is")
    # Parse args
    args = parser.parse_args()
    extension = "csv"
    data_dir = args.datadir
    print(data_dir)
    # Gather files
    all_fnames = [i for i in glob.glob(f"{data_dir}*.{extension}")]
    dfs = []
    for f in all_fnames:
        print(f)
        dfs.append(pd.read_csv(f, header=0))
    combined_csv = pd.concat(dfs)
    combined_csv.to_csv(f"{data_dir}model_fits.csv",index=False,encoding='utf-8-sig')
    

def main():
    parser = argparse.ArgumentParser(
            description="Combine all CSVs in a diretory into one CSV")
    parser.add_argument('datadir',help="Where the data is")
    # Parse args
    args = parser.parse_args()
    extension = "csv"
    data_dir = args.datadir
    # Gather files
    all_fnames = [i for i in glob.glob(f"{data_dir}*.{extension}")]
    combined_csv = pd.concat([pd.read_csv(f) for f in all_fnames])
    combined_csv.to_csv(f"{data_dir}data.csv", index=False, encoding='utf-8-sig')

if __name__ == "__main__":
        main_cluster()