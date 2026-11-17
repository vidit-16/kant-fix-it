"""Experiments in the codebase environment: one JSON line per run.

    uv run python -m evortgs.cb_experiments cbpilot
    uv run python -m evortgs.cb_experiments E9
"""

from __future__ import annotations

import itertools
import json
import multiprocessing as mp
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


def spec(name, seed, *, gamma, n=6, gate="kappa", kappa=0.0, instrument=None, level=0.0,
         split="holdout", kind="evolve", gens=40):
    return dict(exp=name, seed=seed, gamma=gamma, n=n, gate=gate, kappa=kappa,
                instrument=instrument, level=level, split=split, kind=kind, gens=gens)


def run_one(sp: dict) -> dict:
    t0 = time.perf_counter()
    cfg = CodebaseConfig(n=sp["n"], conceal_cost=sp["gamma"])
    sampler = DevSampler(cfg, split="pilot" if sp["split"] == "pilot" else "dev")
    if sp["kind"] == "planner":
        profile = planner(sampler, sp["seed"])
        hist, sims = [], (11 ** 3 + 9 ** 3) * 64
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
    raise SystemExit(f"unknown experiment {which}")


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
        with mp.Pool() as pool, path.open("w", encoding="utf-8") as f:
            for i, rec in enumerate(pool.imap_unordered(run_one, specs), 1):
                rec["commit"], rec["dirty"] = commit, dirty
                f.write(json.dumps(rec) + "\n")
                f.flush()
                if i % 20 == 0 or i == len(specs):
                    print(f"{which}: {i}/{len(specs)} runs, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
