"""Locked holdout evaluation. Never imported by the evolution loop."""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from .scenarios import FAMILIES, WorldConfig, holdout_set, make_scenario
from .sim import Costs, Profile, simulate

HOLDOUT_PER_FAMILY = 100


@lru_cache(maxsize=None)
def _holdout(cfg: WorldConfig, family: str, split: str = "holdout"):
    if split == "holdout":
        return tuple(holdout_set(cfg, family, HOLDOUT_PER_FAMILY))
    return tuple(make_scenario(cfg, family, split, 900_000_000 + i)
                 for i in range(HOLDOUT_PER_FAMILY))


def evaluate(cfg: WorldConfig, profile: Profile, costs: Costs, split: str = "holdout") -> dict:
    """Mean holdout metrics per family, normalised by total payment value."""
    out = {}
    for fam in FAMILIES:
        scns = _holdout(cfg, fam, split)
        sysc, unset, delay, liq, miss = [], [], [], [], []
        bank = np.zeros(cfg.n)
        for s in scns:
            r = simulate(s, profile, costs, check=True)
            v = r.total_value
            sysc.append(r.system_cost / v)
            unset.append(r.unsettled_value / v)
            delay.append(r.delay_value_ticks / v)
            liq.append(sum(r.liquidity) / v)
            miss.append(r.missed_value / v)
            bank += np.asarray(r.cost) / v
        out[fam] = {
            "system_cost": float(np.mean(sysc)),
            "unsettled": float(np.mean(unset)),
            "delay_ticks": float(np.mean(delay)),
            "liquidity": float(np.mean(liq)),
            "missed": float(np.mean(miss)),
            "bank_cost": (bank / len(scns)).tolist(),
        }
    return out
