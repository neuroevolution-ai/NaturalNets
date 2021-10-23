import os
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


directory = os.path.join('../Simulation_Results', '2021-03-20_00-38-46')

with open(os.path.join(directory, "Log.txt")) as file:
    log = file.readlines()

log = log[34:2534]
log = [log_entry.split() for log_entry in log]

log_df = pd.DataFrame(log, columns=["gen", "min", "mean", "max", "best", "elapsed time (s)"])
log_df = log_df.astype(np.float32)
print(log_df)

x_values = log_df["gen"].tolist()
y_values = log_df["best"].tolist()

plt.plot(x_values, y_values)
plt.xlabel("Generations")
plt.ylabel("Mean Reward")

plt.show()

print("Done")