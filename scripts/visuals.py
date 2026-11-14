"""Authored concept comparisons. These are explanations, not observed results."""
CARDS = [
    ('Observed world', 'One outcome per person', 'Counterfactual world', 'The same person under another treatment'),
    ('Association', 'Different people received different treatments', 'Intervention', 'Compare treatment choices for a common population'),
    ('Time zero', 'Eligibility, assignment and follow-up align', 'Treatment definition', 'Specify versions, duration and comparator'),
    ('Common cause', 'Preparation → training; preparation → score', 'Adjustment', 'Compare within baseline preparation groups'),
    ('Before selection', 'Skill → admission ← luck', 'After selection', 'Knowing admission can link skill and luck'),
    ('Total effect', 'Include the pathway through practice', 'Controlled direct effect', 'Hold practice at a specified value'),
    ('One target population', 'Use the same group proportions twice', 'Two treatment means', 'Subtract the standardised untreated mean'),
    ('Common treatment choice', 'Smaller inverse-probability weight', 'Uncommon treatment choice', 'Larger inverse-probability weight'),
    ('Weak overlap', 'A few people carry most of the weight', 'No overlap', 'A required treatment comparison is absent'),
    ('ATT', 'Average effects over treated people', 'ATE', 'Average effects over the full target population'),
    ('Treated change', 'Policy plus untreated time trend', 'Comparison change', 'Proxy for that untreated trend under assumptions'),
    ('Near the cutoff', 'Compare neighbouring assignment scores', 'Far from the cutoff', 'Generalisation needs additional assumptions'),
    ('Invitation effect', 'Change in outcome caused by encouragement', 'Attendance effect', 'Wald ratio targets compliers under IV assumptions'),
    ('Precision', 'How much would an estimator vary?', 'Identification', 'Does the contrast answer the causal question?'),
    ('Sensitivity scenario', 'Specify a prevalence gap and outcome effect', 'Scientific judgement', 'Assess whether that scenario is plausible'),
    ('Target population', 'Everyone the question concerns', 'Observed cases', 'People whose outcomes remain available'),
    ('Transport', 'Effects may depend on the population mix', 'Interference', 'Your treatment can affect another person'),
    ('Calculation', 'Exact source, inputs and output', 'Causal claim', 'Target, design, assumptions and limitations'),
]
def illustration(lesson, namespace, stdout):
    from pathlib import Path
    import json
    course=json.loads((Path(__file__).resolve().parents[1]/'src/course.json').read_text())
    index=next(i for i,l in enumerate(course['lessons']) if l['slug']==lesson['slug'])
    a,b,c,d=CARDS[index]
    return dict(kind='comparison', title='See the distinction', cards=[[a,b],[c,d]],
                conclusion='', caption='Authored conceptual comparison; not measured evidence.')
