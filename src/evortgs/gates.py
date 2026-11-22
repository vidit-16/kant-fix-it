"""Environment-agnostic form of the gated evolution loop in ``evolve.py``.

The gate logic, random streams, budget accounting and history are line for line
those of ``evolve.evolve``; the only change is that scenarios and costs come from
two callables, so the same gates can run in any environment. A test checks that,
given the payment environment, this loop reproduces ``evolve.evolve`` exactly.

``batch(start, count)`` returns a sliceable scenario batch of the base family on
a development split. ``costs(batch, profile)`` returns an array of shape
(S, n, 2): real cost and private cost (real cost plus any transfer the agent is
charged). Neither may give access to held-out scenarios or the evaluator.
"""

from __future__ import annotations

from typing import Callable

import numpy as np

from .evolve import EvoConfig, EvoResult, _clip, _t_ok, random_profile

# Scales on which the universalized counterfactual applies "the same change" to
# every agent. "linear" is the original additive shift in policy units; the others
# apply the same shift in g(x) and map back, x_j' = g^-1(g(x_j) + g(x_i') - g(x_i)).
_EPS = 0.05
SCALES = {
    "linear": None,
    "log": (lambda x: np.log(x + _EPS), lambda y: np.exp(y) - _EPS),
    "sqrt": (np.sqrt, np.square),
    "logit": (lambda x: np.log((x + _EPS) / (1.0 + _EPS - x)),
              lambda y: ((1.0 + _EPS) * np.exp(y) - _EPS) / (1.0 + np.exp(y))),
    # E12 corrections, added after an independent review (E11's own scales above
    # are kept unchanged so its records reproduce):
    # "sqrt" squares g(x_j) + step even when that is negative, which reflects a
    # step below zero into a step the other way; "sqrt_fixed" stops at zero.
    "sqrt_fixed": (np.sqrt, lambda y: np.square(np.maximum(y, 0.0))),
    # "linear" broadcasts the raw proposed delta d (the registered E1-E10 rule);
    # the scales above use the proposer's realized change after clipping.
    # "linear_realized" is linear with the realized change, to match them.
    "linear_realized": None,
}


def _universal(cur, i, cand, d, n, dim, scale):
    """Profile in which every agent makes agent i's change, measured on ``scale``."""
    if scale == "linear":
        return tuple(tuple(_clip(cur[j][a] + d[a]) for a in range(dim)) for j in range(n))
    if scale == "linear_realized":
        step = [cand[a] - cur[i][a] for a in range(dim)]
        return tuple(cand if j == i else tuple(_clip(cur[j][a] + step[a]) for a in range(dim))
                     for j in range(n))
    g, ginv = SCALES[scale]
    step = [float(g(cand[a]) - g(cur[i][a])) for a in range(dim)]
    return tuple(cand if j == i else
                 tuple(_clip(float(ginv(g(cur[j][a]) + step[a]))) for a in range(dim))
                 for j in range(n))


def evolve_env(batch: Callable, costs: Callable, n: int, dim: int, cfg: EvoConfig,
               seed: int, init=None, scale: str = "linear") -> EvoResult:
    if scale not in SCALES:
        raise ValueError(f"unknown scale {scale!r}")
    rng = np.random.default_rng([seed, 7919])
    profile = init if init is not None else random_profile(rng, n, dim)
    res = EvoResult(profile=profile)
    S = 2 * cfg.M

    for g in range(cfg.generations):
        scns = batch(seed * 100_000 + g * S, S)
        frac = g / max(1, cfg.generations - 1)
        sig = cfg.sigma + (cfg.sigma_end - cfg.sigma) * frac
        deltas = rng.normal(0.0, sig, size=(n, cfg.K, dim))
        base = costs(scns, profile)
        res.sims += S
        gen_cost = float(base[:, :, 0].sum(axis=1).mean())
        new_profile = list(profile)
        accepted = 0
        for i in range(n):
            cur = tuple(new_profile) if cfg.sequential else profile
            if cfg.sequential and i > 0:
                base = costs(scns, cur)
                res.sims += S
            kappa = cfg.kappa_by_bank[i] if cfg.kappa_by_bank else cfg.kappa
            best_score, best_pol = 0.0, None
            for k in range(cfg.K):
                d = deltas[i, k]
                cand = tuple(_clip(cur[i][a] + d[a]) for a in range(dim))
                uni = tuple(cand if j == i else cur[j] for j in range(n))
                allp = None
                if cfg.gate in ("welfare_universal",) or (cfg.gate == "kappa" and kappa > 0.0):
                    allp = _universal(cur, i, cand, d, n, dim,
                                      scale if cfg.gate == "kappa" else "linear")
                if cfg.gate == "kappa":
                    if kappa <= 0.0:
                        c = costs(scns, uni)
                        sv = c[:, i, 1] - base[:, i, 1]
                        score = float(sv.mean()) if _t_ok(sv, cfg.min_t) else 0.0
                    elif kappa >= 1.0:
                        c = costs(scns, allp)
                        sv = c[:, i, 1] - base[:, i, 1]
                        score = float(sv.mean()) if _t_ok(sv, cfg.min_t) else 0.0
                    else:
                        h = cfg.M
                        cu = costs(scns[:h], uni)
                        ck = costs(scns[h:], allp)
                        score = float((1 - kappa) * (cu[:, i, 1] - base[:h, i, 1]).mean()
                                      + kappa * (ck[:, i, 1] - base[h:, i, 1]).mean())
                elif cfg.gate == "welfare":
                    c = costs(scns, uni)
                    sv = c[:, :, 0].sum(axis=1) - base[:, :, 0].sum(axis=1)
                    score = float(sv.mean()) if _t_ok(sv, cfg.min_t) else 0.0
                elif cfg.gate == "welfare_universal":
                    c = costs(scns, allp)
                    score = float((c[:, :, 0].sum(axis=1) - base[:, :, 0].sum(axis=1)).mean())
                elif cfg.gate == "noharm":
                    c = costs(scns, uni)
                    sv = c[:, i, 1] - base[:, i, 1]
                    own = float(sv.mean()) if _t_ok(sv, cfg.min_t) else 0.0
                    others = float(((c[:, :, 1].sum(axis=1) - c[:, i, 1])
                                    - (base[:, :, 1].sum(axis=1) - base[:, i, 1])).mean())
                    score = own if others <= 0.0 else 0.0
                else:
                    raise ValueError(f"unknown gate {cfg.gate!r}")
                res.sims += S
                if score < best_score:
                    best_score, best_pol = score, cand
            if best_pol is not None:
                new_profile[i] = best_pol
                accepted += 1
        res.history.append({
            "gen": g,
            "dev_system_cost": gen_cost,
            "accepted": accepted,
            "profile": [list(p) for p in profile],
        })
        profile = tuple(new_profile)
    res.profile = profile
    return res
