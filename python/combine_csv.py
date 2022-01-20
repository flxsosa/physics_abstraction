import pandas as pd
import glob

extension = "csv"
data_dir = "pilot3/"
all_fnames = [i for i in glob.glob(f"{data_dir}*.{extension}")]
combined_csv = pd.concat([pd.read_csv(f) for f in all_fnames])
combined_csv.to_csv(f"{data_dir}data.csv", index=False, encoding='utf-8-sig')