"""Experiments in the codebase environment: one JSON line per run.

    uv run python -m evortgs.cb_experiments cbpilot
    uv run python -m evortgs.cb_experiments E9
"""

from __future__ import annotations

import itertools
import json
import multiprocessing as mp
import os
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np

from .cb_evaluate import evaluate
from .codebase import CodebaseConfig, DevSampler, private_cost, simulate
from .evolve import EvoConfig
from .gates import evolve_env

CONFIRM_SEEDS = range(0, 20)
PILOT_SEEDS = range(1000, 1006)


def make_costs(cfg: CodebaseConfig, instrument: str | None, level: float):
    def costs(b, profile):
        o = simulate(b, profile, cfg)
        out = np.empty((len(b), cfg.n, 2))
        out[:, :, 0] = o.cost
        out[:, :, 1] = private_cost(o, instrument, level)
        return out
    return costs


def planner(sampler: DevSampler, seed: int, batch: int = 64) -> tuple:
    """Reference: exhaustive symmetric grid, then a finer grid around the best point.

    Social cost only, on development scenarios of the given seed.
    """
    cfg = sampler.cfg
    b = sampler.batch(50_000_000 + seed * 1000, batch)

    def f(p):
        o = simulate(b, [p] * cfg.n, cfg)
        return float((o.system_cost / o.nominal).mean())

    g = np.linspace(0.0, 1.0, 11)
    best = min(itertools.product(g, g, g), key=f)
    fine = np.linspace(-0.08, 0.08, 9)
    cands = [tuple(float(min(1.0, max(0.0, best[a] + d[a]))) for a in range(3))
             for d in itertools.product(fine, fine, fine)]
    best = min(cands, key=f)
    return tuple(tuple(best) for _ in range(cfg.n))


def planner_asym(sampler: DevSampler, seed: int, batch: int = 64, sweeps: int = 3):
    """Reference for unequal agents: the symmetric planner, then coordinate descent.

    Each agent in turn is set to its best (s, q) on a grid, with m = 0 (concealment
    only lowers output and raises debt, so it never helps the social cost), holding
    the others fixed; then a finer pass on s. Social cost only, development data.
    Returns the profile and the number of simulations used.
    """
    cfg = sampler.cfg
    b = sampler.batch(50_000_000 + seed * 1000, batch)

    def f(P):
        o = simulate(b, P, cfg)
        return float((o.system_cost / o.nominal).mean())

    P = list(planner(sampler, seed, batch))
    cur, sims = f(P), (11 ** 3 + 9 ** 3 + 1) * batch
    grid = [(s, 0.0, q) for s in np.linspace(0, 1, 21) for q in (0.0, 0.25, 0.5, 0.75, 1.0)]
    for _ in range(sweeps):
        for i in range(cfg.n):
            for p in grid:
                Q = P[:i] + [p] + P[i + 1:]
                v = f(Q)
                sims += batch
                if v < cur - 1e-12:
                    cur, P = v, Q
    for i in range(cfg.n):
        for ds in np.linspace(-0.05, 0.05, 11):
            s = float(min(1.0, max(0.0, P[i][0] + ds)))
            Q = P[:i] + [(s, P[i][1], P[i][2])] + P[i + 1:]
            v = f(Q)
            sims += batch
            if v < cur - 1e-12:
                cur, P = v, Q
    return tuple(tuple(float(x) for x in p) for p in P), sims


def spec(name, seed, *, gamma, n=6, gate="kappa", kappa=0.0, instrument=None, level=0.0,
         split="holdout", kind="evolve", gens=40, het=None, skew=None):
    d = dict(exp=name, seed=seed, gamma=gamma, n=n, gate=gate, kappa=kappa,
             instrument=instrument, level=level, split=split, kind=kind, gens=gens)
    if het is not None:
        d["het"] = het
    if skew is not None:
        d["skew"] = skew
    return d


def run_one(sp: dict) -> dict:
    t0 = time.perf_counter()
    cfg = CodebaseConfig(n=sp["n"], conceal_cost=sp["gamma"], heterogeneity=sp.get("het", 0.0),
                         exposure_skew=sp.get("skew", 0.0))
    sampler = DevSampler(cfg, split="pilot" if sp["split"] == "pilot" else "dev")
    if sp["kind"] == "planner":
        profile = planner(sampler, sp["seed"])
        hist, sims = [], (11 ** 3 + 9 ** 3) * 64
    elif sp["kind"] == "planner_asym":
        profile, sims = planner_asym(sampler, sp["seed"])
        hist = []
    else:
        ecfg = EvoConfig(generations=sp["gens"], gate=sp["gate"], kappa=sp["kappa"])
        r = evolve_env(sampler.batch, make_costs(cfg, sp["instrument"], sp["level"]),
                       cfg.n, 3, ecfg, sp["seed"])
        profile, sims = r.profile, r.sims
        hist = [{"gen": h["gen"], "dev_system_cost": h["dev_system_cost"],
                 "accepted": h["accepted"]} for h in r.history]
        sp = {**sp, "evo": asdict(ecfg)}
    ev = evaluate(cfg, profile, split=sp["split"])
    return {**sp, "env": asdict(cfg), "profile": [list(p) for p in profile], "sims": sims,
            "history": hist, "eval": ev, "seconds": round(time.perf_counter() - t0, 2)}


GATES = (("kappa", 0.0), ("kappa", 1.0), ("welfare", 0.0), ("welfare_universal", 0.0))


def experiments(which: str) -> list[dict]:
    S = []
    if which == "cbpilot":
        grids = {"proxy": (0.1, 0.2, 0.4, 0.8), "activity": (0.25, 0.5, 0.75),
                 "surface": (1.0, 2.0, 4.0, 8.0), "ambient": (0.5, 1.0, 1.5, 2.0)}
        for seed in PILOT_SEEDS:
            for gamma in (0.25, 1.0):
                for n in (6, 12):
                    kw = dict(gamma=gamma, n=n, split="pilot")
                    for g, k in GATES:
                        S.append(spec("cbpilot", seed, gate=g, kappa=k, **kw))
                    for inst, levels in grids.items():
                        if n == 12 and inst in ("activity", "surface"):
                            continue
                        for lev in levels:
                            S.append(spec("cbpilot", seed, instrument=inst, level=lev, **kw))
                    S.append(spec("cbpilot", seed, kind="planner", gate="planner", **kw))
        return S
    if which == "cbpilot2":  # heterogeneity pilot, primary concealment regime
        grids = {"proxy": (0.1, 0.2, 0.4, 0.8), "surface": (1.0, 2.0, 4.0, 8.0),
                 "ambient": (0.5, 1.0, 1.5, 2.0)}
        for seed in PILOT_SEEDS:
            for het in (0.75, 1.5):
                kw = dict(gamma=0.25, het=het, split="pilot")
                for k in (0.0, 0.5, 1.0):
                    S.append(spec("cbpilot2", seed, kappa=k, **kw))
                S.append(spec("cbpilot2", seed, gate="welfare", **kw))
                for inst, levels in grids.items():
                    for lev in levels:
                        S.append(spec("cbpilot2", seed, instrument=inst, level=lev, **kw))
                S.append(spec("cbpilot2", seed, kind="planner", gate="planner", **kw))
                S.append(spec("cbpilot2", seed, kind="planner_asym", gate="planner_asym", **kw))
        return S
    if which == "cbpilot3":  # exposure-heterogeneity pilot (size heterogeneity preserved symmetry)
        grids = {"proxy": (0.1, 0.2, 0.4, 0.8), "surface": (1.0, 2.0, 4.0, 8.0),
                 "ambient": (0.5, 1.0, 1.5, 2.0)}
        for seed in PILOT_SEEDS:
            for skew in (0.75, 1.5):
                kw = dict(gamma=0.25, skew=skew, split="pilot")
                for k in (0.0, 0.5, 1.0):
                    S.append(spec("cbpilot3", seed, kappa=k, **kw))
                S.append(spec("cbpilot3", seed, gate="welfare", **kw))
                for inst, levels in grids.items():
                    for lev in levels:
                        S.append(spec("cbpilot3", seed, instrument=inst, level=lev, **kw))
                S.append(spec("cbpilot3", seed, kind="planner", gate="planner", **kw))
                S.append(spec("cbpilot3", seed, kind="planner_asym", gate="planner_asym", **kw))
        return S
    if which == "E9":  # frozen in docs/PREREGISTRATION_E9.md
        for seed in CONFIRM_SEEDS:
            for gamma in (0.25, 1.0):
                for n in (6, 12):
                    kw = dict(gamma=gamma, n=n)
                    for inst, levels in E9_GRIDS.items():
                        if n == 12 and inst in ("activity", "surface"):
                            continue
                        for lev in levels:
                            S.append(spec("E9", seed, instrument=inst, level=lev, **kw))
                    for g, k in GATES:
                        if n == 12 and g == "welfare_universal":
                            continue
                        S.append(spec("E9", seed, gate=g, kappa=k, **kw))
                    S.append(spec("E9", seed, kind="planner", gate="planner", **kw))
        return S
    raise SystemExit(f"unknown experiment {which}")


# Frozen after the pilot; see docs/PREREGISTRATION_E9.md.
E9_GRIDS = {"proxy": (0.1, 0.2, 0.4, 0.8), "activity": (0.25, 0.5, 0.75),
            "surface": (1.0, 2.0, 4.0, 8.0), "ambient": (0.5, 1.0, 1.5, 2.0)}


def main(argv=None):
    argv = argv or sys.argv[1:]
    out_dir = Path("runs")
    out_dir.mkdir(exist_ok=True)
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "src"],
                                    capture_output=True, text=True).stdout.strip())
    except OSError:
        commit, dirty = "", True
    for which in argv:
        specs = experiments(which)
        path = out_dir / f"{which}.jsonl"
        t0 = time.time()
        workers = int(os.environ.get("EVO_WORKERS", "0")) or None
        with mp.Pool(workers) as pool, path.open("w", encoding="utf-8") as f:
            for i, rec in enumerate(pool.imap_unordered(run_one, specs), 1):
                rec["commit"], rec["dirty"] = commit, dirty
                f.write(json.dumps(rec) + "\n")
                f.flush()
                if i % 20 == 0 or i == len(specs):
                    print(f"{which}: {i}/{len(specs)} runs, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
