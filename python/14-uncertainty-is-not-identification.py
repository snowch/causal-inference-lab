# Seeded simulation; not evidence about a real population.
import numpy as np
rng = np.random.default_rng(14)
n = 2000
l = rng.binomial(1, 0.5, n)
a = rng.binomial(1, np.where(l == 1, 0.8, 0.2))
y = 40 + 20*l + 2*a + rng.normal(0, 3, n)
def contrast(indices):
    aa, yy = a[indices], y[indices]
    return yy[aa == 1].mean() - yy[aa == 0].mean()
estimate = contrast(np.arange(n))
boot = [contrast(rng.integers(0, n, n)) for _ in range(400)]
print('Unadjusted contrast:', round(estimate, 2))
print('Approximate 95% bootstrap interval:', np.round(np.quantile(boot, [0.025, 0.975]), 2))
print('Authored causal effect:', 2)

import matplotlib.pyplot as plt
plt.hist(boot, bins=25, color='#607ac1', label='Bootstrap contrasts')
plt.axvline(2, color='#3a8b77', linewidth=2, label='Authored causal effect')
plt.xlabel('Unadjusted outcome difference (points)')
plt.ylabel('Bootstrap resamples')
plt.title('Seeded simulation: precision does not remove bias')
plt.legend()
