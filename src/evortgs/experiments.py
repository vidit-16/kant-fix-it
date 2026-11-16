"""Experiment runner: one JSON line per run, everything needed to reproduce it."""

from __future__ import annotations

import json
import multiprocessing as mp
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

from .evaluate import evaluate
from .evolve import EvoConfig, evolve, planner_symmetric
from .scenarios import DevSampler, WorldConfig
from .sim import Costs

T = 20
CONFIRM_SEEDS = range(0, 20)
PILOT_SEEDS = range(1000, 1006)


def costs_for(delay_day: float) -> Costs:
    """delay_day = cost of delaying one unit for a whole day, in units of cL."""
    return Costs(cL=1.0, cD=delay_day / T, cX=2.0, cE=10.0)


def spec(name, seed, *, delay_day, n=6, het=0.0, gate="kappa", kappa=0.0, fee=0.0,
         sequential=False, defector=None, split="holdout", kind="evolve", gens=40):
    return dict(exp=name, seed=seed, delay_day=delay_day, n=n, het=het, gate=gate,
                kappa=kappa, fee=fee, sequential=sequential, defector=defector,
                split=split, kind=kind, gens=gens)


def run_one(sp: dict) -> dict:
    t0 = time.perf_counter()
    world = WorldConfig(n=sp["n"], T=T, heterogeneity=sp["het"])
    costs = costs_for(sp["delay_day"])
    dev_split = "pilot" if sp["split"] == "pilot" else "dev"
    sampler = DevSampler(world, split=dev_split)
    if sp["kind"] == "planner":
        profile, hist, sims = planner_symmetric(sampler, costs, sp["seed"]), [], 300 * 32
    else:
        kb = None
        if sp["defector"] is not None:
            kb = tuple(0.0 if i == sp["defector"] else sp["kappa"] for i in range(sp["n"]))
        ecfg = EvoConfig(generations=sp["gens"], gate=sp["gate"], kappa=sp["kappa"], fee=sp["fee"],
                         sequential=sp["sequential"], kappa_by_bank=kb)
        r = evolve(sampler, costs, ecfg, sp["seed"])
        profile, sims = r.profile, r.sims
        hist = [{"gen": h["gen"], "dev_system_cost": h["dev_system_cost"],
                 "accepted": h["accepted"]} for h in r.history]
        sp = {**sp, "evo": asdict(ecfg)}
    ev = evaluate(world, profile, costs, split=sp["split"])
    return {**sp, "profile": [list(p) for p in profile], "sims": sims, "history": hist,
            "eval": ev, "seconds": round(time.perf_counter() - t0, 2)}


def experiments(which: str) -> list[dict]:
    S = []
    if which == "pilot":
        for d in (0.1, 0.5, 2.0, 6.0):
            for seed in PILOT_SEEDS:
                for g, k in (("kappa", 0.0), ("kappa", 1.0), ("welfare", 0.0)):
                    S.append(spec("pilot", seed, delay_day=d, gate=g, kappa=k, split="pilot"))
            S.append(spec("pilot", 1000, delay_day=d, kind="planner", gate="planner", split="pilot"))
        return S
    D = PRIMARY_DELAY_DAY
    for seed in CONFIRM_SEEDS:
        if which == "E1":  # gates, homogeneous banks, primary regime
            for k in (0.0, 0.25, 0.5, 0.75, 1.0):
                S.append(spec("E1", seed, delay_day=D, kappa=k))
            S.append(spec("E1", seed, delay_day=D, gate="welfare"))
            S.append(spec("E1", seed, delay_day=D, gate="welfare_universal"))
            S.append(spec("E1", seed, delay_day=D, gate="noharm"))
            for fee in (1.0, 2.0, 4.0, 8.0):
                S.append(spec("E1", seed, delay_day=D, fee=fee))
            S.append(spec("E1", seed, delay_day=D, kind="planner", gate="planner"))
        elif which == "E2":  # heterogeneity
            for het in (0.75, 1.5):
                for g, k in (("kappa", 0.0), ("kappa", 1.0), ("welfare", 0.0),
                             ("welfare_universal", 0.0), ("noharm", 0.0)):
                    S.append(spec("E2", seed, delay_day=D, het=het, gate=g, kappa=k))
                S.append(spec("E2", seed, delay_day=D, het=het, kind="planner", gate="planner"))
        elif which == "E3":  # cost regime
            for d in OTHER_DELAY_DAYS:
                for g, k in (("kappa", 0.0), ("kappa", 1.0), ("welfare", 0.0)):
                    S.append(spec("E3", seed, delay_day=d, gate=g, kappa=k))
                S.append(spec("E3", seed, delay_day=d, kind="planner", gate="planner"))
        elif which == "E4":  # one private defector among universalizing banks
            for het in (0.0, 1.5):
                S.append(spec("E4", seed, delay_day=D, het=het, kappa=1.0, defector=seed % 6))
        elif which == "E5":  # robustness: sequential updates, larger network
            for g, k in (("kappa", 0.0), ("kappa", 1.0), ("welfare", 0.0)):
                S.append(spec("E5seq", seed, delay_day=D, gate=g, kappa=k, sequential=True))
                S.append(spec("E5n10", seed, delay_day=D, n=10, gate=g, kappa=k))
            S.append(spec("E5n10", seed, delay_day=D, n=10, kind="planner", gate="planner"))
        elif which == "E6":  # three times the search budget
            if seed < 10:
                for g, k in (("kappa", 0.0), ("kappa", 1.0), ("welfare", 0.0)):
                    S.append(spec("E6", seed, delay_day=D, gate=g, kappa=k, gens=120))
        else:
            raise SystemExit(f"unknown experiment {which}")
    return S


# Frozen after the pilot; see docs/PREREGISTRATION.md.
PRIMARY_DELAY_DAY = 0.5
OTHER_DELAY_DAYS = (0.1, 2.0, 6.0)


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
                if i % 20 == 0 or i == len(specs):
                    print(f"{which}: {i}/{len(specs)} runs, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
