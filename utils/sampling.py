import random


def weighted_sample(candidates, probabilities):
    total = sum(probabilities)
    if total == 0:
        return random.choice(candidates)
    probabilities = [p / total for p in probabilities]
    return random.choices(candidates, weights=probabilities)[0]
