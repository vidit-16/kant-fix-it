"""Pre-registered analysis of E13 (docs/PREREGISTRATION_E13.md). Frozen with the protocol.

    uv run python -m evortgs.analysis_e13          # writes runs/results_e13.json

Reads runs/E13.jsonl, runs/e13_lock.json and, if present, runs/E13sens.jsonl.
Halts before any interpretation if a structural invariant fails.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
from scipy import stats

from . import e13
from .codebase import make_batch

MARGIN = 0.002
FAMILY_ALPHA = 0.05
N_PRIMARY = 4
ALPHA_EACH = FAMILY_ALPHA / N_PRIMARY


def _load(path):
    p = Path(path)
    return [json.loads(x) for x in p.read_text().splitlines()] if p.exists() else []


def _index(recs):
    out = {}
    for r in recs:
        key = (r["seed"], r["effort"], r["skew"], r["arm"])
        if key in out:
            raise SystemExit(f"duplicate run {key}")
        out[key] = r
    return out


def interval(d: np.ndarray, alpha: float = ALPHA_EACH) -> dict:
    n = len(d)
    m, sd = float(d.mean()), float(d.std(ddof=1))
    h = float(stats.t.ppf(1 - alpha / 2, n - 1) * sd / np.sqrt(n))
    lo, hi = m - h, m + h
    if lo > MARGIN:
        verdict = "gate advantage"
    elif hi < -MARGIN:
        verdict = "comparator advantage"
    elif lo >= -MARGIN and hi <= MARGIN:
        verdict = "practical equivalence"
    else:
        verdict = "inconclusive"
    return {"mean": m, "sd": sd, "lo": lo, "hi": hi, "n": n, "verdict": verdict}


def _paired(idx, seeds, effort, skew, a, b):
    """Per-seed score(a) - score(b); None if any pair is missing."""
    d = []
    for s in seeds:
        ra, rb = idx.get((s, effort, skew, a)), idx.get((s, effort, skew, b))
        if ra is None or rb is None:
            return None
        d.append(e13.score(ra) - e13.score(rb))
    return np.array(d)


def one_sided(d: np.ndarray) -> float:
    """p for H1: mean(d) > 0."""
    return float(stats.ttest_1samp(d, 0.0, alternative="greater").pvalue)


def holm(ps: dict) -> dict:
    order = sorted(ps, key=ps.get)
    out, running = {}, 0.0
    for k, name in enumerate(order):
        adj = min(1.0, (len(ps) - k) * ps[name])
        running = max(running, adj)
        out[name] = {"p": ps[name], "p_holm": running, "supported": running < FAMILY_ALPHA}
    return out


# ---------------------------------------------------------------- secondary test 3

def marginal_errors(lock: dict) -> dict:
    """Mean absolute error of each mechanism's own-score contrast against the exact
    unilateral welfare contrast, on held-back dev seeds with oracle labels.

    Level-1 POOL's contrast is multiplied by n (its effort-off calibration); the tuned
    direct charge (lowest validation mean among direct and directrole) and the
    centred contract are on the unit own-cost scale. Ambient level 1 is reported
    as the exact-identity check (its error should be zero up to rounding).
    """
    res = {}
    for skew in e13.SKEWS:
        cfg = e13.config(e13.EFFORT, skew)
        means = lock["selected"][str(skew)]["means"]
        direct = min((a for a in means if a.startswith("direct")), key=lambda a: means[a])
        lev = float(direct.split("_")[1])
        mechs = {
            "pool": (e13.Mechanism(cfg, "pool", 1.0), cfg.n),
            "direct": (e13.Mechanism(cfg, "direct", lev, role=direct.startswith("directrole"),
                                     scale=lock["direct_scale"][str(skew)]), 1.0),
            "contract": (e13.Mechanism(cfg, "contract", anchor=lock["anchor"]), 1.0),
            "ambient": (e13.Mechanism(cfg, "ambient", 1.0), 1.0),
        }
        per_seed = {k: [] for k in mechs}
        for seed in e13.ORACLE_SEEDS:
            rng = np.random.default_rng([seed, 6007])
            P = rng.random((cfg.n, 3))
            b = make_batch(cfg, "base", e13.DEV_SPLIT, e13.ORACLE_START + (seed % 1000) * 16, 16)
            errs = {k: [] for k in mechs}
            base = {k: m(b, P) for k, (m, _) in mechs.items()}
            for i in range(cfg.n):
                for _ in range(4):
                    Q = P.copy()
                    Q[i] = np.clip(P[i] + rng.normal(0.0, 0.1, 3), 0.0, 1.0)
                    for k, (m, c) in mechs.items():
                        cq = m(b, Q)
                        dW = float((cq[:, :, 0].sum(axis=1) - base[k][:, :, 0].sum(axis=1)).mean())
                        ds = float((cq[:, i, 1] - base[k][:, i, 1]).mean())
                        errs[k].append(abs(c * ds - dW))
            for k in mechs:
                per_seed[k].append(float(np.mean(errs[k])))
        res[str(skew)] = {"direct_arm": direct, **{k: v for k, v in per_seed.items()}}
    return res


# ---------------------------------------------------------------- main

def main():
    lock = json.loads(e13.LOCK.read_text())
    recs = _load("runs/E13.jsonl")
    idx = _index(recs)
    seeds = list(e13.CONFIRM_SEEDS)
    out = {"lock": {k: lock[k] for k in ("anchor", "direct_scale", "big_M")},
           "selected": {sk: {r: lock["selected"][sk][r]["spec"]["arm"] for r in ("strict", "ambient")}
                        for sk in lock["selected"]}}

    # structural invariants: stop before interpretation if any fails
    inv = {}
    for skew in e13.SKEWS:
        same = [idx[(s, 0.0, skew, "pool_1.0")]["profile"] == idx[(s, 0.0, skew, "ambient_1.0")]["profile"]
                for s in seeds if (s, 0.0, skew, "pool_1.0") in idx and (s, 0.0, skew, "ambient_1.0") in idx]
        inv[f"pool_equals_ambient_effort_off_skew{skew}"] = f"{sum(same)}/{len(same)}"
        if not all(same):
            raise SystemExit(f"invariant failed: effort-off pool/ambient trajectories differ at skew {skew}")
    strict_kinds = ("pool", "direct", "contract")
    worst = max((r["settle"]["balance_max_abs"] for r in recs if r["kind"] in strict_kinds), default=0.0)
    inv["max_abs_strict_balance_residual"] = worst
    if worst > 1e-6:
        raise SystemExit(f"invariant failed: strict transfers do not balance ({worst})")
    sims = {r["search_sims"] for r in recs if r["M"] == 8}
    inv["search_sims"] = sorted(sims)
    if sims != {e13.GENERATIONS * 16 * 25}:
        raise SystemExit("invariant failed: agent search budgets differ")
    out["invariants"] = inv

    # primary: four contrasts, comparator minus gate, Bonferroni familywise 95%
    prim, missing = {}, []
    for skew in e13.SKEWS:
        for role in ("strict", "ambient"):
            arm = lock["selected"][str(skew)][role]["spec"]["arm"]
            d = _paired(idx, seeds, e13.EFFORT, skew, arm, "kantian")
            name = f"{role}_skew{skew}"
            if d is None:
                missing.append(name)
                prim[name] = {"arm": arm, "verdict": "inconclusive (incomplete pairs)"}
                continue
            prim[name] = {"arm": arm, **interval(d)}
    out["primary"] = prim
    strict_hi = [prim[f"strict_skew{sk}"].get("hi") for sk in e13.SKEWS]
    out["kill_criterion"] = {
        "rule": "close the gate-advantage line for budget-balanced settings if the strict "
                "comparator's simultaneous upper bound is <= +0.002 in both effort-on cells",
        "upper_bounds": strict_hi,
        "met": all(h is not None and h <= MARGIN for h in strict_hi)}

    # secondary, Holm over three one-sided tests
    sec = {}
    g = lambda eff, sk, a, b: _paired(idx, seeds, eff, sk, a, b)
    d1 = np.mean([g(e13.EFFORT, sk, "pool_1.0", "ambient_1.0") - g(0.0, sk, "pool_1.0", "ambient_1.0")
                  for sk in e13.SKEWS], axis=0)
    d2 = g(e13.EFFORT, 1.5, "kantian", "ambient_1.0") - g(e13.EFFORT, 0.0, "kantian", "ambient_1.0")
    me = marginal_errors(lock)
    dd = np.mean([np.array(me[str(sk)]["pool"]) - np.array(me[str(sk)]["direct"]) for sk in e13.SKEWS], axis=0)
    dc = np.mean([np.array(me[str(sk)]["pool"]) - np.array(me[str(sk)]["contract"]) for sk in e13.SKEWS], axis=0)
    ps = {"S1_effort_widens_pool_ambient_gap": one_sided(d1),
          "S2_unequal_exposure_widens_gate_ambient_gap": one_sided(d2),
          "S3_direct_and_contract_beat_pool_marginal_error": max(one_sided(dd), one_sided(dc))}
    sec["tests"] = holm(ps)
    sec["estimates"] = {"S1": float(d1.mean()), "S2": float(d2.mean()),
                        "S3_direct": float(dd.mean()), "S3_contract": float(dc.mean())}
    sec["marginal_errors"] = {sk: {k: (float(np.mean(v)) if isinstance(v, list) else v)
                                   for k, v in me[sk].items()} for sk in me}
    out["secondary"] = sec

    # descriptive: every arm in every cell
    desc = {}
    for r in recs:
        cell = f"effort{r['effort']}_skew{r['skew']}"
        desc.setdefault(cell, {}).setdefault(r["arm"], []).append(r)
    table = {}
    for cell, arms in desc.items():
        table[cell] = {}
        for arm, rs in arms.items():
            sc = [e13.score(r) for r in rs]
            eff = [np.mean([r["eval"][f].get("effort_cost", 0.0) for f in e13.FAMILIES]) for r in rs]
            P = np.array([r["profile"] for r in rs])   # (seeds, n, 3)
            # settlement burden against the paired private run
            worse, tot = 0, 0
            for r in rs:
                pr = idx.get((r["seed"], r["effort"], r["skew"], "private"))
                if pr is None:
                    continue
                mine = np.array(r["settle"]["agent_real"]) + np.array(r["settle"]["agent_transfer"])
                worse += int((mine > np.array(pr["settle"]["agent_real"]) + 1e-12).sum())
                tot += len(mine)
            table[cell][arm] = {
                "n": len(rs), "cost": float(np.mean(sc)), "effort_cost": float(np.mean(eff)),
                "policy_by_agent": P.mean(axis=0).round(4).tolist(),
                "worse_than_private_share": worse / tot if tot else None,
                "abs_transfer_p95": float(np.mean([r["settle"]["abs_transfer_p95"] for r in rs])),
                "abs_transfer_max": float(np.max([r["settle"]["abs_transfer_max"] for r in rs])),
                "search_sims": int(np.median([r["search_sims"] for r in rs])),
                "total_sims": int(np.median([r["total_sims"] for r in rs])),
                "seconds": float(np.median([r["seconds"] for r in rs]))}
    out["descriptive"] = table

    # sensitivities, labelled, outside inference
    sens = _index(_load("runs/E13sens.jsonl"))
    if sens:
        both = {**idx, **sens}
        sres = {}
        for skew in e13.SKEWS:
            st = lock["selected"][str(skew)]["strict"]["spec"]
            pairs = {"noise": (st["arm"] + "_noise" if st["kind"] in ("direct", "contract") else st["arm"],
                               "kantian_noise"),
                     "cap": (st["arm"] + "_cap", "kantian"),
                     "compute_matched": (st["arm"], "kantian_bigM")}
            for name, (a, b) in pairs.items():
                d = _paired(both, seeds, e13.EFFORT, skew, a, b)
                sres[f"{name}_skew{skew}"] = {"arms": [a, b], **(interval(d) if d is not None else {})}
        out["sensitivities"] = sres

    Path("runs/results_e13.json").write_text(json.dumps(out, indent=1))
    print(json.dumps({"primary": prim, "kill": out["kill_criterion"], "secondary": sec["tests"]}, indent=1))


if __name__ == "__main__":
    main()
