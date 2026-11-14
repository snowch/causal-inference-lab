# Invented teaching data; not evidence about a real population.
import numpy as np
# Control means for low/high preparation.
control_mean = np.array([40., 70.])
treated_group = np.array([0, 1, 1, 1])
treated_score = np.array([42., 80., 80., 80.])
matched_differences = treated_score - control_mean[treated_group]
att = matched_differences.mean()
print('Matched differences:', matched_differences)
print('ATT:', att)
print('ATE in an equal-mix population:', np.mean([2., 10.]))
