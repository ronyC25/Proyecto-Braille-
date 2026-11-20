def sus_score(responses):
    """SUS: 10 items on a 1-5 scale. Odd items are positive, even items negative."""
    if len(responses) != 10:
        raise ValueError("SUS requiere 10 respuestas")
    total = 0
    for index, response in enumerate(responses, start=1):
        if index % 2 == 1:
            total += response - 1
        else:
            total += 5 - response
    return total * 2.5


def nasa_tlx(scores, weights=None):
    """NASA-TLX global score. scores: six subscales 0-100."""
    if len(scores) != 6:
        raise ValueError("NASA-TLX requiere 6 subescalas")
    if weights is None:
        return sum(scores) / 6
    if len(weights) != 6:
        raise ValueError("Se requieren 6 pesos")
    total_weight = sum(weights)
    if total_weight == 0:
        return 0.0
    return sum(score * weight for score, weight in zip(scores, weights)) / total_weight
