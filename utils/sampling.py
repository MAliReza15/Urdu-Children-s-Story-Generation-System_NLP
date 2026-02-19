import random

def weighted_sample(candidates, probabilities):
    total = sum(probabilities)
    if total == 0:
        return random.choice(candidates)
    probabilities = [p / total for p in probabilities]
    return random.choices(candidates, weights=probabilities)[0]


def weighted_sample_with_temperature(candidates, probabilities, temperature=1.0, top_k=None):
    """
    Weighted sampling with temperature scaling and optional top-k filtering.
    :param candidates: list of token IDs
    :param probabilities: list of probabilities corresponding to candidates
    :param temperature: float >0, lower = more deterministic
    :param top_k: int or None, limit sampling to top-k probable candidates
    """
    if sum(probabilities) == 0:
        return random.choice(candidates)

    # Apply temperature scaling
    if temperature <= 0:
        temperature = 1.0
    probs = [p ** (1.0 / temperature) for p in probabilities]
    total = sum(probs)
    probs = [p / total for p in probs]

    # Apply top-k filtering
    if top_k is not None and top_k < len(probs):
        # get indices of top_k probabilities
        top_indices = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)[:top_k]
        top_probs = [probs[i] for i in top_indices]
        top_total = sum(top_probs)
        top_probs = [p / top_total for p in top_probs]
        top_candidates = [candidates[i] for i in top_indices]
        return random.choices(top_candidates, weights=top_probs)[0]

    return random.choices(candidates, weights=probs)[0]

def weighted_sample_top_p(candidates, probabilities, top_p=0.9, temperature=1.0):
    """
    Weighted sampling with nucleus (top-p) and temperature scaling.
    :param candidates: list of token IDs
    :param probabilities: list of probabilities corresponding to candidates
    :param top_p: cumulative probability threshold (0 < top_p <= 1)
    :param temperature: float >0, lower = more deterministic
    """
    if sum(probabilities) == 0:
        return random.choice(candidates)

    # Apply temperature scaling
    if temperature <= 0:
        temperature = 1.0
    probs = [p ** (1.0 / temperature) for p in probabilities]
    total = sum(probs)
    probs = [p / total for p in probs]

    # Sort candidates by probability descending
    sorted_indices = sorted(range(len(probs)), key=lambda i: probs[i], reverse=True)
    sorted_probs = [probs[i] for i in sorted_indices]
    sorted_candidates = [candidates[i] for i in sorted_indices]

    # Compute cumulative probability and select cutoff
    cumulative = 0.0
    cutoff = 0
    for i, p in enumerate(sorted_probs):
        cumulative += p
        if cumulative >= top_p:
            cutoff = i + 1
            break

    # Keep only top-p candidates
    top_candidates = sorted_candidates[:cutoff]
    top_probs = sorted_probs[:cutoff]
    top_total = sum(top_probs)
    top_probs = [p / top_total for p in top_probs]

    return random.choices(top_candidates, weights=top_probs)[0]
