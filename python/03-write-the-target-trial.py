# Invented teaching data; not evidence about a real population.
protocols = [
    dict(name='Vague', treatment='any future training', time_zero=None,
         outcome='later performance', follow_up=None),
    dict(name='Specified', treatment='offer an 8-week course versus no offer',
         time_zero='eligibility and offer date', outcome='score at 12 weeks',
         follow_up='12 weeks for both groups'),
]
for p in protocols:
    missing = [k for k in ['time_zero', 'follow_up'] if not p[k]]
    print(p['name'], 'missing fields:', missing)
print('Checked for values in time_zero and follow_up only.')
