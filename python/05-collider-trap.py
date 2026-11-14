# Invented teaching data; not evidence about a real population.
import numpy as np
skill = np.array([0, 0, 1, 1])
luck = np.array([0, 1, 0, 1])
admitted = (skill + luck) >= 1
print('Population correlation:', np.corrcoef(skill, luck)[0, 1])
selected_correlation = np.corrcoef(skill[admitted], luck[admitted])[0, 1]
print('Correlation after selecting admission:', selected_correlation)
