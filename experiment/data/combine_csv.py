import pandas as pd
import glob

extension = "csv"
all_fnames = [i for i in glob.glob("*.{}".format(extension))]
combined_csv = pd.concat([pd.read_csv(f) for f in all_fnames])
combined_csv.to_csv("data.csv", index=False, encoding='utf-8-sig')