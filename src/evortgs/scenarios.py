"""Scenario generation with a hard development / holdout seed split.

Every scenario is a pure function of (config, family, split, index). The split
tag is mixed into the seed, so development and holdout streams can never
collide. The evolution code is handed only a development sampler.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np

from .sim import Scenario

FAMILIES = ("base", "surge", "outage", "late_heavy", "hub")
_FAMILY_ID = {f: i for i, f in enumerate(FAMILIES)}
_SPLIT_ID = {"dev": 11, "holdout": 23, "pilot": 37}

AMOUNT_SCALE = 1000
AMOUNT_SIGMA = 1.0


@dataclass(frozen=True)
class WorldConfig:
    n: int = 6
    T: int = 20
    payments_per_bank: int = 20
    heterogeneity: float = 0.0  # bank size weight ~ rank ** -heterogeneity
    p_urgent: float = 0.15


def size_weights(cfg: WorldConfig) -> np.ndarray:
    w = np.arange(1, cfg.n + 1, dtype=float) ** (-cfg.heterogeneity)
    return w / w.sum()


def expected_outflow(cfg: WorldConfig) -> tuple[int, ...]:
    """Expected gross daily outflow per bank under the base family.

    This is what a bank 'knows' about its typical day. Shock families do not
    change it, so shocks are genuinely unanticipated.
    """
    mean_amt = AMOUNT_SCALE * math.exp(AMOUNT_SIGMA**2 / 2)
    total = cfg.n * cfg.payments_per_bank * mean_amt
    return tuple(int(round(w * total)) for w in size_weights(cfg))


def make_scenario(cfg: WorldConfig, family: str, split: str, index: int) -> Scenario:
    rng = np.random.default_rng(
        [_SPLIT_ID[split], _FAMILY_ID[family], index, cfg.n, cfg.T,
         cfg.payments_per_bank, int(round(cfg.heterogeneity * 1000))]
    )
    n, T = cfg.n, cfg.T
    w = size_weights(cfg)
    P = n * cfg.payments_per_bank
    sigma = AMOUNT_SIGMA
    outage: tuple[tuple[int, int, int], ...] = ()

    send_w = w.copy()
    recv_w = w.copy()
    if family == "surge":
        hit = int(rng.integers(n))
        send_w[hit] *= 2.5
        send_w /= send_w.sum()
        P = int(round(P * 1.25))
    elif family == "hub":
        hubs = rng.choice(n, size=2, replace=False)
        recv_w[hubs] *= 4.0
        recv_w /= recv_w.sum()
    elif family == "late_heavy":
        sigma = 1.5
    elif family == "outage":
        hit = int(rng.integers(n))
        start = int(rng.integers(2, T // 2))
        outage = ((hit, start, start + T // 4),)

    senders = rng.choice(n, size=P, p=send_w)
    pay = []
    for s in senders:
        pr = recv_w.copy()
        pr[s] = 0.0
        pr /= pr.sum()
        r = int(rng.choice(n, p=pr))
        mu = -(sigma**2 - AMOUNT_SIGMA**2) / 2  # keep the mean amount fixed
        amt = max(1, int(round(AMOUNT_SCALE * rng.lognormal(mu, sigma))))
        if family == "late_heavy":
            arr = int(min(T - 2, math.floor(rng.beta(3.0, 1.5) * (T - 1))))
        else:
            arr = int(rng.integers(0, T - 1))
        if rng.random() < cfg.p_urgent:
            dl = min(T - 1, arr + int(rng.integers(0, 3)))
        else:
            dl = -1
        pay.append((int(s), r, amt, arr, dl))
    pay.sort(key=lambda p: (p[3], p[0], p[1], p[2]))
    arrivals: list[list[int]] = [[] for _ in range(T)]
    for k, p in enumerate(pay):
        arrivals[p[3]].append(k)
    return Scenario(
        n=n, T=T, exp_out=expected_outflow(cfg), pay=tuple(pay),
        arrivals=tuple(tuple(a) for a in arrivals), outage=outage,
    )


class DevSampler:
    """The only scenario source the evolution loop is given.

    It can produce base-family development scenarios and nothing else.
    """

    def __init__(self, cfg: WorldConfig, split: str = "dev"):
        if split == "holdout":
            raise ValueError("the evolution loop may not sample holdout scenarios")
        self.cfg = cfg
        self._split = split

    def batch(self, start: int, count: int) -> list[Scenario]:
        return [make_scenario(self.cfg, "base", self._split, start + i) for i in range(count)]


def holdout_set(cfg: WorldConfig, family: str, count: int) -> list[Scenario]:
    return [make_scenario(cfg, family, "holdout", i) for i in range(count)]
