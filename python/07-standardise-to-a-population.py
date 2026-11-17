# Invented teaching data; not evidence about a real population.
import numpy as np
mu0 = np.array([40., 70.])
mu1 = np.array([42., 80.])
target = np.array([0.8, 0.2])
assert np.isclose(target.sum(), 1)
standardised0 = target @ mu0
standardised1 = target @ mu1
ate = standardised1 - standardised0
print('Target means without/with:', round(standardised0, 2), round(standardised1, 2))
print('Target average difference:', round(ate, 2))
print('Equal-mix difference:', np.mean(mu1 - mu0))
