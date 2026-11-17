# Invented teaching data; not evidence about a real population.
policy_effect = 4
group_specific_trend = 0
control_before, control_after = 50, 56
treated_before = 40
treated_after = treated_before + 6 + policy_effect + group_specific_trend
did = (treated_after - treated_before) - (control_after - control_before)
print('Treated group change:', treated_after - treated_before)
print('Comparison group change:', control_after - control_before)
print('Difference-in-differences:', did)
print('Authored effect:', policy_effect)
