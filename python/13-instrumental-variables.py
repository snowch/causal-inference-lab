# Invented teaching data; not evidence about a real population.
import numpy as np
# Never-takers, compliers, always-takers: two of each.
a0 = np.array([0, 0, 0, 0, 1, 1])
a1 = np.array([0, 0, 1, 1, 1, 1])
attendance_effect = 6
direct_invitation_effect = 0
y0 = 40 + attendance_effect * a0
y1 = 40 + attendance_effect * a1 + direct_invitation_effect
first_stage = (a1-a0).mean()
reduced_form = (y1-y0).mean()
wald = reduced_form / first_stage
print('Attendance change:', round(first_stage, 3))
print('Invitation outcome change:', reduced_form)
print('Wald ratio:', wald)
