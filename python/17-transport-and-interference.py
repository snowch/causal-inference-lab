# Invented teaching data; not evidence about a real population.
import numpy as np
# New and experienced learners.
group_effects = np.array([8., 2.])
study_mix = np.array([0.8, 0.2])
destination_mix = np.array([0.2, 0.8])
print('Study average effect:', round(study_mix @ group_effects, 2))
print('Destination average under transport assumptions:', round(destination_mix @ group_effects, 2))
print('This calculation assumes the same group effects apply in both settings.')
