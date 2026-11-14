# Invented teaching data; not evidence about a real population.
import numpy as np
preparation = np.array([0, 0, 0, 0, 1, 1, 1, 1])
training = np.array([0, 0, 0, 1, 0, 1, 1, 1])
y0 = 40 + 30 * preparation
y1 = y0.copy()
observed = np.where(training == 1, y1, y0)
naive = observed[training == 1].mean() - observed[training == 0].mean()
print('Observed difference:', naive)
print('Model ATE:', (y1 - y0).mean())

import matplotlib.pyplot as plt
plt.bar(['Observed difference', 'Model causal effect'], [naive, (y1-y0).mean()], color=['#607ac1', '#3a8b77'])
plt.ylabel('Score points')
plt.title('Invented data: association versus intervention')
