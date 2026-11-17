# Learning design

Audience: curious adults who can read Python lists, functions and loops. Means, differences and proportions are introduced before estimators. Scientific Method Lab is a recommended precursor, not a requirement.

Outcome: specify a causal question, explain an identification strategy, estimate an effect under stated assumptions, challenge it, and write a qualified conclusion.

Six modules of three investigations: counterfactual questions; diagrams and adjustment; standardisation and weighting; design-based comparisons; uncertainty and robustness; reporting and transfer. Each lesson has one observable outcome, inspectable invented or simulated inputs, a prediction, executable Python, a deliberate change, and a fresh application with two hints and explanatory feedback.

Misconceptions to challenge: prediction equals intervention; adjusting for everything helps; a propensity score guarantees comparability; significance establishes identification; a natural experiment is automatically random; a null diagnostic proves an assumption.

The simulations deliberately expose ground truth so learners can separate statistical precision from identification. Real observational data do not supply this oracle. Report targets, positivity, consistency, exchangeability and interference boundaries explicitly.

## Learner-flow pass

Keep the existing prerequisites and one outcome per lesson. The published code
prepares the example. The learner runs it, finds the named output, changes the
specified input in the editor, and compares the new result with the first run.
The worked result remains available for reading without Python.

Name each comparison at the point of use. For matching, compare the average
effect among the treated with the average in the equal-mix population after
changing who is treated. For overlap, distinguish the weight concentration
diagnostic from the separate empty-cell example. In the remaining lessons, keep
the transfer case independent and give it a first hint about the relevant
evidence and a second hint about how to use it.
