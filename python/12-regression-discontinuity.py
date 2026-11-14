# Invented teaching data; not evidence about a real population.
import numpy as np
score = np.linspace(-10, 10, 2002)
a = (score >= 0).astype(int)
effect = 5
y = 50 + 0.8 * score + effect * a
for width in [5., 1., 0.2]:
    left = (score < 0) & (score >= -width)
    right = (score >= 0) & (score <= width)
    print('Window:', width, 'Raw local difference:', round(y[right].mean()-y[left].mean(), 3))
print('True discontinuity at cutoff:', effect)

import matplotlib.pyplot as plt
plt.plot(score[score < 0], y[score < 0], label='Untreated')
plt.plot(score[score >= 0], y[score >= 0], label='Treated')
plt.axvline(0, color='grey', linestyle='--', label='Assignment cutoff')
plt.xlabel('Assignment score relative to cutoff')
plt.ylabel('Outcome points')
plt.title('Authored sharp discontinuity model')
plt.legend()
