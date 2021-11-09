import pandas as pd

data = pd.read_csv("data.csv")

responses = data[data.task == 'response']
non_timeout = responses[responses.rt < 3000]
timeout = responses[responses.rt >= 3000]
