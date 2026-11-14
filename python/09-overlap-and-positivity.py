# Invented teaching data; not evidence about a real population.
import numpy as np
weights = np.array([1., 1., 1., 1., 1., 1., 1., 1., 1., 100.])
ess = weights.sum()**2 / np.sum(weights**2)
# Rows are baseline groups; columns are untreated and treated counts.
counts = np.array([[20, 20], [0, 40]])
print('Records:', len(weights), 'Weight-based effective sample size:', round(ess, 2))
print('Groups with an empty treatment cell:', np.where((counts == 0).any(axis=1))[0])
