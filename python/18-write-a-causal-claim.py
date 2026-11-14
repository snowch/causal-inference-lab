# Invented teaching data; not evidence about a real population.
import numpy as np
# Rows: low/high preparation; columns: untreated/treated.
means = np.array([[40., 45.], [70., 75.]])
counts = np.array([[80, 20], [20, 80]])
target = counts.sum(axis=1) / counts.sum()
raw_means = (means*counts).sum(axis=0) / counts.sum(axis=0)
raw = raw_means[1] - raw_means[0]
adjusted = target @ (means[:, 1]-means[:, 0])
print('Invented target proportions:', target)
print('Unadjusted contrast (points):', raw)
print('Standardised contrast (points):', adjusted)
print('Causal interpretation requires justified assumptions; no uncertainty interval computed.')
