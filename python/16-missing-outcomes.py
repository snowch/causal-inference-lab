# Invented teaching data; not evidence about a real population.
import numpy as np
y0 = np.array([40., 50., 60., 70.])
y1 = y0 + 5
observed0 = np.array([True, True, True, True])
observed1 = np.array([False, False, True, True])
full_effect = (y1-y0).mean()
complete_case = y1[observed1].mean() - y0[observed0].mean()
print('Full model effect:', full_effect)
print('Available-case contrast:', complete_case)
print('Observed fractions:', observed0.mean(), observed1.mean())
