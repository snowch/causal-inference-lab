# Invented teaching data; not evidence about a real population.
import numpy as np
without = np.array([40, 50, 60, 70, 80, 90])
with_training = np.array([48, 56, 64, 72, 80, 88])
effects = with_training - without
ate = effects.mean()
print('Individual model effects:', effects)
print('Population ATE (score points):', ate)
