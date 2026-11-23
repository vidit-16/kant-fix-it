"""Locked holdout evaluation for the codebase environment. Never imported by evolution code."""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from .codebase import FAMILIES, CodebaseConfig, make_batch, simulate

HOLDOUT_PER_FAMILY = 100


@lru_cache(maxsize=None)
def _holdout(cfg: CodebaseConfig, family: str, split: str = "holdout", start: int | None = None):
    if start is None:   # E1-E12 blocks; E13 passes its own fresh block
        start = 0 if split == "holdout" else 900_000_000
    return make_batch(cfg, family, split, start, HOLDOUT_PER_FAMILY)


def evaluate(cfg: CodebaseConfig, profile, split: str = "holdout", start: int | None = None) -> dict:
    """Mean metrics per family; costs normalised by nominal value."""
    out = {}
    for fam in FAMILIES:
        b = _holdout(cfg, fam, split, start)
        o = simulate(b, profile, cfg, check=True)
        coup = o.visible + o.hidden
        out[fam] = {
            "system_cost": float((o.system_cost / o.nominal).mean()),
            "agent_cost": (o.cost / o.nominal[:, None] * cfg.n).mean(axis=0).tolist(),
            "debt": float(o.debt.mean()),
            "incidents": float(o.incidents.mean()),
            "hidden_share": float(o.hidden.sum() / coup.sum()) if coup.sum() > 0 else 0.0,
        }
        if cfg.effort:
            out[fam]["effort_cost"] = float((o.effort.sum(axis=1) / o.nominal).mean())
    P = np.asarray(profile)
    out["policy_mean"] = P.mean(axis=0).tolist()
    return out
