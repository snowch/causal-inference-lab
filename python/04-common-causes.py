# Invented teaching data; not evidence about a real population.
import numpy as np
# Rows: low/high preparation; columns: untreated/treated.
means = np.array([[40., 45.], [70., 75.]])
counts = np.array([[90, 10], [10, 90]])
observed = (means * counts).sum(axis=0) / counts.sum(axis=0)
within = means[:, 1] - means[:, 0]
print('Overall difference:', observed[1] - observed[0])
print('Within-preparation differences:', within)
print('Equal-population standardised difference:', within.mean())
