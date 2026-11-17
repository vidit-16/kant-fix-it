"""Population self-evolution under a configurable acceptance gate.

Each generation every bank proposes ``K`` bounded mutations of its own policy,
scores them by simulation on fresh development scenarios, and a *gate* decides
whether the best one replaces the incumbent. All gates spend exactly the same
number of simulations per candidate (``2 * M``); they differ only in which
counterfactual they simulate and whose costs they are allowed to read.

Gates
-----
``kappa`` (0..1)  Own-cost gate of an agent with degree of morality kappa:
                  score = (1-kappa) * d_own(unilateral) + kappa * d_own(universal)
                  where 'unilateral' changes only this bank and 'universal'
                  applies the same parameter shift to every bank. kappa=0 is the
                  private gate; kappa=1 is the universalization (Kantian) gate.
                  Reads only the proposing bank's own cost.
``welfare``       score = change in total system cost under unilateral change.
                  Needs every bank's cost (a central observer).
``welfare_universal``  score = change in total system cost when every bank
                  applies the same shift. Separates the effect of *joint moves*
                  from the effect of *whose cost is read*.
``noharm``        accept the best private improvement among candidates that do
                  not raise the summed cost of the other banks.

``fee`` is an operator surcharge on delay cost (a transfer, so it enters the
private cost the gates read but not the social cost that is reported).
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .scenarios import DevSampler
from .sim import Costs, Profile, Scenario, simulate


@dataclass(frozen=True)
class EvoConfig:
    generations: int = 40
    K: int = 4            # candidates per bank per generation
    M: int = 8            # half-batch of scenarios; each candidate costs 2*M sims
    sigma: float = 0.15   # mutation scale at generation 0
    sigma_end: float = 0.03  # mutation scale at the last generation (linear decay)
    gate: str = "kappa"   # kappa | welfare | welfare_universal | noharm
    kappa: float = 0.0
    fee: float = 0.0
    min_t: float = 0.0    # accept only if the paired t-statistic of the score is below -min_t
    sequential: bool = False  # banks update one after another instead of simultaneously
    # per-bank kappa override, e.g. a single private defector among Kantian banks
    kappa_by_bank: tuple[float, ...] | None = None


@dataclass
class EvoResult:
    profile: Profile
    history: list[dict] = field(default_factory=list)
    sims: int = 0


def _clip(x: float) -> float:
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else x


def _costs(scns: list[Scenario], profile: Profile, costs: Costs, fee: float) -> np.ndarray:
    """Per-scenario, per-bank [real, private] costs, shape (S, n, 2)."""
    out = np.empty((len(scns), len(profile), 2))
    for j, s in enumerate(scns):
        r = simulate(s, profile, costs)
        out[j, :, 0] = r.cost
        out[j, :, 1] = np.asarray(r.cost) + fee * np.asarray(r.delay_cost)
    return out


def _t_ok(v: np.ndarray, min_t: float) -> bool:
    if min_t <= 0.0:
        return True
    sd = v.std(ddof=1)
    return sd > 0 and v.mean() / (sd / np.sqrt(len(v))) < -min_t


def random_profile(rng: np.random.Generator, n: int) -> Profile:
    return tuple(tuple(float(x) for x in rng.random(3)) for _ in range(n))


def evolve(sampler: DevSampler, costs: Costs, cfg: EvoConfig, seed: int,
           init: Profile | None = None) -> EvoResult:
    n = sampler.cfg.n
    rng = np.random.default_rng([seed, 7919])
    profile: Profile = init if init is not None else random_profile(rng, n)
    res = EvoResult(profile=profile)
    S = 2 * cfg.M

    for g in range(cfg.generations):
        # scenario indices depend on (seed, generation) only -> paired across gates
        scns = sampler.batch(start=seed * 100_000 + g * S, count=S)
        frac = g / max(1, cfg.generations - 1)
        sig = cfg.sigma + (cfg.sigma_end - cfg.sigma) * frac
        deltas = rng.normal(0.0, sig, size=(n, cfg.K, 3))
        base = _costs(scns, profile, costs, cfg.fee)
        res.sims += S
        gen_cost = float(base[:, :, 0].sum(axis=1).mean())
        new_profile = list(profile)
        accepted = 0
        order = range(n)
        for i in order:
            cur = tuple(new_profile) if cfg.sequential else profile
            if cfg.sequential and i > 0:
                base = _costs(scns, cur, costs, cfg.fee)
                res.sims += S
            kappa = cfg.kappa_by_bank[i] if cfg.kappa_by_bank else cfg.kappa
            best_score, best_pol = 0.0, None
            for k in range(cfg.K):
                d = deltas[i, k]
                cand = tuple(_clip(cur[i][a] + d[a]) for a in range(3))
                uni = tuple(cand if j == i else cur[j] for j in range(n))
                if cfg.gate == "kappa":
                    if kappa <= 0.0:
                        c = _costs(scns, uni, costs, cfg.fee)
                        sv = c[:, i, 1] - base[:, i, 1]
                        score = float(sv.mean()) if _t_ok(sv, cfg.min_t) else 0.0
                    elif kappa >= 1.0:
                        allp = tuple(tuple(_clip(cur[j][a] + d[a]) for a in range(3))
                                     for j in range(n))
                        c = _costs(scns, allp, costs, cfg.fee)
                        sv = c[:, i, 1] - base[:, i, 1]
                        score = float(sv.mean()) if _t_ok(sv, cfg.min_t) else 0.0
                    else:
                        h = cfg.M
                        allp = tuple(tuple(_clip(cur[j][a] + d[a]) for a in range(3))
                                     for j in range(n))
                        cu = _costs(scns[:h], uni, costs, cfg.fee)
                        ck = _costs(scns[h:], allp, costs, cfg.fee)
                        score = float((1 - kappa) * (cu[:, i, 1] - base[:h, i, 1]).mean()
                                      + kappa * (ck[:, i, 1] - base[h:, i, 1]).mean())
                elif cfg.gate == "welfare":
                    c = _costs(scns, uni, costs, cfg.fee)
                    sv = c[:, :, 0].sum(axis=1) - base[:, :, 0].sum(axis=1)
                    score = float(sv.mean()) if _t_ok(sv, cfg.min_t) else 0.0
                elif cfg.gate == "welfare_universal":
                    allp = tuple(tuple(_clip(cur[j][a] + d[a]) for a in range(3))
                                 for j in range(n))
                    c = _costs(scns, allp, costs, cfg.fee)
                    score = float((c[:, :, 0].sum(axis=1) - base[:, :, 0].sum(axis=1)).mean())
                elif cfg.gate == "noharm":
                    c = _costs(scns, uni, costs, cfg.fee)
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


def planner_symmetric(sampler: DevSampler, costs: Costs, seed: int,
                      n_random: int = 150, n_refine: int = 150, batch: int = 32) -> Profile:
    """Reference: best single policy imposed on every bank, found on dev scenarios."""
    n = sampler.cfg.n
    rng = np.random.default_rng([seed, 104729])
    scns = sampler.batch(start=50_000_000 + seed * 1000, count=batch)

    def f(p):
        prof = tuple(p for _ in range(n))
        return sum(simulate(s, prof, costs).system_cost for s in scns) / len(scns)

    best, best_v = None, float("inf")
    for _ in range(n_random):
        p = tuple(float(x) for x in rng.random(3))
        v = f(p)
        if v < best_v:
            best, best_v = p, v
    sig = 0.15
    for t in range(n_refine):
        p = tuple(_clip(best[a] + rng.normal(0, sig)) for a in range(3))
        v = f(p)
        if v < best_v:
            best, best_v = p, v
        if (t + 1) % 50 == 0:
            sig *= 0.5
    return tuple(best for _ in range(n))
