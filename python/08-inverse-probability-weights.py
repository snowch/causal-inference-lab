# Invented teaching data; not evidence about a real population.
import numpy as np
baseline = np.repeat([0, 1], 10)
a = np.array([1]*2 + [0]*8 + [1]*8 + [0]*2)
e = np.where(baseline == 0, 0.2, 0.8)
treatment_effect = 5
y = 40 + 30 * baseline + treatment_effect * a
weights = np.where(a == 1, 1/e, 1/(1-e))
naive = y[a == 1].mean() - y[a == 0].mean()
ipw = np.average(y[a == 1], weights=weights[a == 1]) - np.average(y[a == 0], weights=weights[a == 0])
print('Observed difference:', naive)
print('Weighted difference:', ipw)
print('Weights:', weights)

import matplotlib.pyplot as plt
fig, ax = plt.subplots()
ax.bar(['Unadjusted', 'Weighted', 'Model effect'], [naive, ipw, treatment_effect], color=['#607ac1', '#3a8b77', '#bd9140'])
ax.set_ylabel('Score points')
ax.set_title('Invented population; known propensity scores')
