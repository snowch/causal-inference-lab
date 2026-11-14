# Invented teaching data; not evidence about a real population.
observed_difference = 4
prevalence_gap = 0.4
for confounder_effect in [0, 5, 10, 15]:
    bias = prevalence_gap * confounder_effect
    corrected = observed_difference - bias
    print('Hypothetical U effect:', confounder_effect,
          'Bias:', bias, 'Remaining contrast:', round(corrected, 2))

import matplotlib.pyplot as plt
u_effects = [0, 5, 10, 15]
remaining = [observed_difference - prevalence_gap * u for u in u_effects]
plt.plot(u_effects, remaining, marker='o')
plt.axhline(0, color='grey', linestyle='--')
plt.xlabel('Hypothetical unmeasured-confounder effect (points)')
plt.ylabel('Remaining contrast (points)')
plt.title('Authored sensitivity scenarios; not measured effects')
