import numpy as np
from scipy.stats import binomtest, friedmanchisquare, wilcoxon


def paired_wilcoxon(x, y):
    return wilcoxon(x, y, alternative="two-sided")


def mcnemar(b, c):
    """McNemar test for paired binary outcomes. b and c are discordant counts."""
    result = binomtest(b, b + c, p=0.5, alternative="two-sided")
    return {"statistic": b, "p_value": result.pvalue}


def friedman(*samples):
    return friedmanchisquare(*samples)


def bootstrap_mean_ci(values, n_resamples=5000, confidence_level=0.95, seed=42):
    values = np.asarray(values, dtype=float)
    rng = np.random.default_rng(seed)
    estimates = [
        np.mean(rng.choice(values, size=len(values), replace=True))
        for _ in range(n_resamples)
    ]
    alpha = (1 - confidence_level) / 2
    return float(np.quantile(estimates, alpha)), float(np.quantile(estimates, 1 - alpha))
