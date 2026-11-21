"""Export fixtures for the browser engine's parity tests.

Run from the repository root: uv run python site/engine/fixtures/export.py
Writes site/engine/fixtures/parity.json. Every number in it comes from the
research code in src/evortgs, so the JavaScript port is tested against the
code that produced the published results.
"""

import json
from pathlib import Path

import numpy as np

from evortgs.cb_experiments import make_costs
from evortgs.codebase import CodebaseConfig, make_batch, simulate
from evortgs.evolve import EvoConfig, random_profile
from evortgs.gates import evolve_env

OUT = Path(__file__).with_name("parity.json")


def batch_json(b):
    return {"S": int(b.cap.shape[0]), "T": int(b.cap.shape[1]), "n": int(b.cap.shape[2]),
            "cap": b.cap.ravel().tolist(), "u": b.u.ravel().tolist(),
            "val": b.val.ravel().tolist(), "mult": b.mult.ravel().tolist(),
            "d0": b.d0.ravel().tolist()}


def cfg_json(cfg):
    return {k: getattr(cfg, k) for k in cfg.__dataclass_fields__}


def main():
    rng = np.random.default_rng(20261121)
    fx = {"simulate": [], "sums": [], "loops": []}

    configs = [CodebaseConfig(), CodebaseConfig(exposure_skew=1.5), CodebaseConfig(conceal_cost=1.0),
               CodebaseConfig(heterogeneity=0.75), CodebaseConfig(n=12)]
    for cfg in configs:
        for fam in ("base", "crunch", "fragile", "spike", "legacy"):
            b = make_batch(cfg, fam, "pilot", 777, 5)
            for _ in range(3):
                prof = rng.random((cfg.n, 3)).round(6).tolist()
                o = simulate(b, prof, cfg)
                fx["simulate"].append({
                    "cfg": cfg_json(cfg), "family": fam, "batch": batch_json(b), "profile": prof,
                    "cost": o.cost.ravel().tolist(), "nominal": o.nominal.tolist(),
                    "charges": o.charges.ravel().tolist(), "debt": o.debt.tolist(),
                    "incidents": o.incidents.tolist(), "visible": o.visible.tolist(),
                    "hidden": o.hidden.tolist()})

    for n in list(range(1, 40)) + [63, 64, 65, 127, 128, 129, 130, 200, 257, 300]:
        a = rng.normal(0, 1, n) * 10 ** rng.uniform(-6, 3)
        fx["sums"].append({"a": a.tolist(), "sum": float(a.sum()), "mean": float(a.mean())})

    cases = [("kappa", 0.0, None, 0.0, "linear", 0.0), ("kappa", 1.0, None, 0.0, "linear", 0.0),
             ("kappa", 0.5, None, 0.0, "linear", 1.5), ("kappa", 1.0, None, 0.0, "logit", 1.5),
             ("kappa", 1.0, None, 0.0, "log", 0.75), ("welfare", 0.0, None, 0.0, "linear", 0.0),
             ("welfare_universal", 0.0, None, 0.0, "linear", 0.0),
             ("kappa", 0.0, "ambient", 1.0, "linear", 1.5), ("kappa", 0.0, "proxy", 0.2, "linear", 0.0),
             ("kappa", 0.0, "surface", 4.0, "linear", 0.0)]
    for gate, kappa, inst, lev, scale, skew in cases:
        cfg = CodebaseConfig(exposure_skew=skew)
        e = EvoConfig(generations=5, K=3, M=4, gate=gate, kappa=kappa)
        seed = 11
        S = 2 * e.M
        batches = [make_batch(cfg, "base", "dev", seed * 100_000 + g * S, S) for g in range(e.generations)]
        r = np.random.default_rng([seed, 7919])
        init = random_profile(r, cfg.n, 3)
        deltas = []
        for g in range(e.generations):
            frac = g / max(1, e.generations - 1)
            sig = e.sigma + (e.sigma_end - e.sigma) * frac
            deltas.append(r.normal(0.0, sig, size=(cfg.n, e.K, 3)).ravel().tolist())
        res = evolve_env(lambda st, ct: make_batch(cfg, "base", "dev", st, ct),
                         make_costs(cfg, inst, lev), cfg.n, 3, e, seed, scale=scale)
        fx["loops"].append({
            "case": f"{gate} k={kappa} {inst}{lev:g} {scale} skew={skew}",
            "cfg": cfg_json(cfg), "evo": {"generations": e.generations, "K": e.K, "M": e.M,
                                          "sigma": e.sigma, "sigma_end": e.sigma_end,
                                          "gate": gate, "kappa": kappa, "scale": scale},
            "instrument": inst, "level": lev, "seed": seed,
            "init": [list(p) for p in init], "deltas": deltas,
            "batches": [batch_json(b) for b in batches],
            "history": [{"dev_system_cost": h["dev_system_cost"], "accepted": h["accepted"],
                         "profile": h["profile"]} for h in res.history],
            "final": [list(p) for p in res.profile], "sims": res.sims})
    OUT.write_text(json.dumps(fx), encoding="utf-8")
    print(f"wrote {OUT} ({OUT.stat().st_size // 1024} KB): "
          f"{len(fx['simulate'])} simulate, {len(fx['sums'])} sums, {len(fx['loops'])} loops")


if __name__ == "__main__":
    main()
