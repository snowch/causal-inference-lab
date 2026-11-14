# Authored structural model; not evidence about a real population.
direct = 3
training_to_practice = 2
practice_to_score = 4
def score(training, practice):
    return direct * training + practice_to_score * practice
natural0 = score(0, 0)
natural1 = score(1, training_to_practice)
total = natural1 - natural0
controlled_direct = score(1, 0) - score(0, 0)
print('Total model effect:', total)
print('Effect with practice held at zero:', controlled_direct)
