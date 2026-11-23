"""E13: the Kantian gate against budget-balanced transfers when effort is off the ledger.

Protocol: docs/PREREGISTRATION_E13.md. Stages, each one JSON line per run:

    uv run python -m evortgs.e13 calib     # dev seeds 2000-2019: direct-charge scale, contract anchor
    uv run python -m evortgs.e13 select    # dev seeds 2100-2119: comparator selection
    uv run python -m evortgs.e13 lock      # writes runs/e13_lock.json from the two stages above
    uv run python -m evortgs.e13 E13       # confirmatory seeds 3000-3019, fresh holdout block
    uv run python -m evortgs.e13 E13sens   # labelled sensitivities

Every mechanism runs under the same pinned search loop (``gates.evolve_env`` logic),
so arms differ only in the private cost an agent's gate reads. Transfers enter that
private cost and never the real cost that is reported.
"""

from __future__ import annotations

import json
import multiprocessing as mp
import os
import subprocess
import sys
import time
from dataclasses import asdict
from pathlib import Path

import numpy as np
from scipy import stats

from .cb_evaluate import FAMILIES, HOLDOUT_PER_FAMILY, evaluate
from .codebase import CodebaseConfig, DevSampler, exposure, make_batch, simulate, sizes
from .evolve import EvoConfig, EvoResult, _clip, random_profile
from .gates import _universal

EFFORT = 0.15
SKEWS = (0.0, 1.5)
GAMMA = 0.25
CALIB_SEEDS = range(2000, 2020)
VALID_SEEDS = range(2100, 2120)
ORACLE_SEEDS = range(2200, 2220)   # held back for secondary test 3
CONFIRM_SEEDS = range(3000, 3020)
CALIB_EVAL_START = 900_000_000     # dev split, evaluation block for calibration
VALID_EVAL_START = 950_000_000     # dev split, evaluation block for selection
ORACLE_START = 980_000_000         # dev split, scenarios for secondary test 3
SCALE_START = 990_000_000          # dev split, scenarios for the direct-charge scale
HOLDOUT_START = 1_000_000          # holdout split, fresh block (E1-E12 used 0-99)
GRID = (0.25, 0.5, 1.0, 1.5, 2.0, 4.0)
ANCHORS = {"zero": (0.0, 0.0, 0.0), "mid": (0.5, 0.0, 0.5)}
NOISE_SD = 0.10
CAP_SHARE = 0.10
SCALE = "linear_realized"          # kappa=1 broadcasts the focal agent's realized clipped change
LOCK = Path("runs/e13_lock.json")
GENERATIONS = 40
# a dry run of the whole pipeline (tests, timing) patches these two to "pilot" so it
# never reads the development evaluation blocks or the confirmatory holdout
DEV_SPLIT = "dev"
CONFIRM_SPLIT = "holdout"


def config(effort: float, skew: float) -> CodebaseConfig:
    return CodebaseConfig(n=6, conceal_cost=GAMMA, exposure_skew=skew, effort=effort)


# ---------------------------------------------------------------- transfers

def load(profile) -> np.ndarray:
    """Verified coupling load per unit capacity, s(1 + eta m); the direct-charge base."""
    P = np.asarray(profile, dtype=float)
    return P[:, 0] * (1.0 + 0.5 * P[:, 1])


def direct_rates(cfg: CodebaseConfig, tau: float, role: bool) -> np.ndarray:
    """Common rate, or role rates tau * n (1 - e_i / sum e) / (n - 1)."""
    n = cfg.n
    if not role:
        return np.full(n, tau)
    e = exposure(cfg) if cfg.exposure_skew else np.ones(n)
    return tau * n * (1.0 - e / e.sum()) / (n - 1)


def direct_transfer(cfg: CodebaseConfig, profile, tau: float, role: bool) -> np.ndarray:
    """t_i = tau_i h_i - (1/(n-1)) sum_{j != i} tau_j h_j; sums to zero, own rebate fixed."""
    th = direct_rates(cfg, tau, role) * load(profile)
    return th - (th.sum() - th) / (cfg.n - 1)


def cap(t: np.ndarray, cfg: CodebaseConfig) -> np.ndarray:
    """Scale each scenario's whole settlement vector so |t_i| <= CAP_SHARE x ex ante nominal."""
    bound = CAP_SHARE * cfg.T * sizes(cfg) * (1.0 + cfg.boost)
    worst = np.max(np.abs(t) / bound, axis=-1, keepdims=True)
    return t / np.maximum(1.0, worst)


class Mechanism:
    """costs(batch, profile) -> (S, n, 2) real and private cost, with a simulation count.

    kinds: none | pool | ambient | direct | contract. ``level`` multiplies pool and
    ambient; for direct it multiplies the development-calibrated scale.
    """

    def __init__(self, cfg: CodebaseConfig, kind: str = "none", level: float = 1.0,
                 role: bool = False, anchor: str = "zero", scale: float = 1.0,
                 capped: bool = False):
        self.cfg, self.kind, self.level, self.role = cfg, kind, level, role
        self.anchor, self.scale, self.capped = ANCHORS[anchor], scale, capped
        self.sims = 0           # every underlying scenario simulation, resets included
        self._b, self._cache = None, {}

    def _sim(self, b, profile):
        key = tuple(tuple(float(x) for x in p) for p in profile)
        if b is not self._b:
            self._b, self._cache = b, {}
        o = self._cache.get(key)
        if o is None:
            o = simulate(b, key, self.cfg)
            self.sims += len(b)
            self._cache[key] = o
        return o

    def transfer(self, b, profile, o) -> np.ndarray:
        cfg, n = self.cfg, self.cfg.n
        if self.kind == "none":
            return np.zeros_like(o.cost)
        if self.kind == "pool":
            y = o.charges[:, :, 1]
            t = self.level * (y - y.mean(axis=1, keepdims=True))
        elif self.kind == "ambient":
            t = self.level * o.charges[:, :, 3]
        elif self.kind == "direct":
            t = np.broadcast_to(direct_transfer(cfg, profile, self.level * self.scale, self.role),
                                o.cost.shape).copy()
        elif self.kind == "contract":
            led = o.cost - o.effort
            E = np.empty_like(led)
            for i in range(n):
                r = [tuple(p) for p in profile]
                r[i] = self.anchor
                lr = self._sim(b, r)
                ledr = lr.cost - lr.effort
                E[:, i] = (led.sum(axis=1) - led[:, i]) - (ledr.sum(axis=1) - ledr[:, i])
            t = E - E.mean(axis=1, keepdims=True)
        else:
            raise ValueError(f"unknown mechanism {self.kind!r}")
        return cap(t, cfg) if self.capped else t

    def __call__(self, b, profile) -> np.ndarray:
        o = self._sim(b, profile)
        out = np.empty((len(b), self.cfg.n, 2))
        out[:, :, 0] = o.cost
        out[:, :, 1] = o.cost + self.transfer(b, profile, o)
        return out

    def settle(self, b, profile):
        """Real cost, transfer and outcome on a fixed batch (for holdout reporting)."""
        o = simulate(b, profile, self.cfg)
        self._b, self._cache = None, {}
        return o, self.transfer(b, profile, o)


# ---------------------------------------------------------------- search loop

def evolve(batch, costs, n: int, cfg: EvoConfig, seed: int, kappa: float,
           noise: float = 0.0) -> EvoResult:
    """``gates.evolve_env`` for kappa in {0, 1}, with optional peer-policy noise in scores.

    With noise = 0 this is line for line the pinned loop (a test checks equality).
    With noise > 0 each agent scores against its own view of the current profile:
    peers j != i at clip(p_j + z_gj), z drawn once per (generation, peer) from a
    stream keyed on the seed alone, so every arm sees the same draws. The focal
    agent's own policy is exact, deployment uses the chosen candidate, and the
    baseline is re-scored on each agent's view (n extra batches per generation).
    """
    rng = np.random.default_rng([seed, 7919])
    profile = random_profile(rng, n, 3)
    res = EvoResult(profile=profile)
    S = 2 * cfg.M
    nrng = np.random.default_rng([seed, 31337])
    for g in range(cfg.generations):
        scns = batch(seed * 100_000 + g * S, S)
        frac = g / max(1, cfg.generations - 1)
        sig = cfg.sigma + (cfg.sigma_end - cfg.sigma) * frac
        deltas = rng.normal(0.0, sig, size=(n, cfg.K, 3))
        z = nrng.normal(0.0, noise, size=(n, 3)) if noise else None
        base = costs(scns, profile)
        res.sims += S
        gen_cost = float(base[:, :, 0].sum(axis=1).mean())
        new_profile = list(profile)
        accepted = 0
        for i in range(n):
            cur = profile
            if noise:
                cur = tuple(cur[i] if j == i else
                            tuple(_clip(cur[j][a] + z[j, a]) for a in range(3)) for j in range(n))
                bi = costs(scns, cur)
                res.sims += S
            else:
                bi = base
            best_score, best_pol = 0.0, None
            for k in range(cfg.K):
                d = deltas[i, k]
                cand = tuple(_clip(cur[i][a] + d[a]) for a in range(3))
                if kappa >= 1.0:
                    prof = _universal(cur, i, cand, d, n, 3, SCALE)
                else:
                    prof = tuple(cand if j == i else cur[j] for j in range(n))
                c = costs(scns, prof)
                score = float((c[:, i, 1] - bi[:, i, 1]).mean())
                res.sims += S
                if score < best_score:
                    best_score, best_pol = score, cand
            if best_pol is not None:
                new_profile[i] = best_pol
                accepted += 1
        res.history.append({"gen": g, "dev_system_cost": gen_cost, "accepted": accepted,
                            "profile": [list(p) for p in profile]})
        profile = tuple(new_profile)
    res.profile = profile
    return res


# ---------------------------------------------------------------- one run

def spec(stage, seed, *, effort, skew, arm, kind="none", level=1.0, role=False,
         anchor="zero", kappa=0.0, noise=0.0, capped=False, M=8, split="holdout"):
    return dict(exp=stage, seed=seed, effort=effort, skew=skew, arm=arm, kind=kind,
                level=level, role=role, anchor=anchor, kappa=kappa, noise=noise,
                capped=capped, M=M, split=split)


def eval_start(sp) -> int:
    return {"calib": CALIB_EVAL_START, "select": VALID_EVAL_START}.get(sp["exp"], HOLDOUT_START)


def settlement_report(cfg, mech: Mechanism, profile, split, start) -> dict:
    """Per-agent real cost and transfer on the evaluation block, normalised like agent_cost."""
    real, tr, frac, bal = [], [], [], 0.0
    for fam in FAMILIES:
        b = make_batch(cfg, fam, split, start, HOLDOUT_PER_FAMILY)
        o, t = mech.settle(b, profile)
        bal = max(bal, float(np.abs(t.sum(axis=1)).max()))
        nom_i = o.nominal[:, None] / cfg.n
        real.append(o.cost / o.nominal[:, None] * cfg.n)
        tr.append(t / o.nominal[:, None] * cfg.n)
        frac.append(np.abs(t) / nom_i)
    real, tr, frac = (np.concatenate(x) for x in (real, tr, frac))
    return {"agent_real": real.mean(axis=0).tolist(), "agent_transfer": tr.mean(axis=0).tolist(),
            "abs_transfer_p95": float(np.quantile(frac, 0.95)),
            "abs_transfer_max": float(frac.max()),
            "balance_max_abs": bal}


def run_one(sp: dict) -> dict:
    t0 = time.perf_counter()
    cfg = config(sp["effort"], sp["skew"])
    sampler = DevSampler(cfg, split=DEV_SPLIT)
    scale = sp.get("scale", 1.0)
    mech = Mechanism(cfg, sp["kind"], sp["level"], sp["role"], sp["anchor"], scale, sp["capped"])
    ecfg = EvoConfig(generations=GENERATIONS, K=4, M=sp["M"], gate="kappa", kappa=sp["kappa"])
    r = evolve(sampler.batch, mech, cfg.n, ecfg, sp["seed"], sp["kappa"], sp["noise"])
    split = CONFIRM_SPLIT if sp["exp"] in ("E13", "E13sens") else DEV_SPLIT
    start = eval_start(sp)
    ev = evaluate(cfg, r.profile, split=split, start=start)
    rep = settlement_report(cfg, Mechanism(cfg, sp["kind"], sp["level"], sp["role"],
                                           sp["anchor"], scale, sp["capped"]),
                            r.profile, split, start)
    return {**sp, "env": asdict(cfg), "evo": asdict(ecfg), "profile": [list(p) for p in r.profile],
            "search_sims": r.sims, "total_sims": mech.sims, "eval_split": split,
            "eval_start": start, "eval": ev, "settle": rep,
            "history": [{k: h[k] for k in ("gen", "dev_system_cost", "accepted")} for h in r.history],
            "seconds": round(time.perf_counter() - t0, 2)}


def score(rec) -> float:
    """Normalised welfare cost: per-scenario W/nominal, family means, equal family weights."""
    return float(np.mean([rec["eval"][f]["system_cost"] for f in FAMILIES]))


# ---------------------------------------------------------------- calibration

def marginal_damage(seed: int, skew: float, batch: int = 32, h: float = 0.05) -> float:
    """Paired finite-difference estimate of d(peers' ledger cost)/d(load) per unit load.

    A uniform random profile from the seed; each agent's s moved by +-h (clipped),
    peers fixed; the change in the other agents' ledger cost over the change in
    the agent's load s(1 + 0.5 m). Development scenarios from their own block.
    """
    cfg = config(EFFORT, skew)
    rng = np.random.default_rng([seed, 4099])
    P = rng.random((cfg.n, 3))
    b = make_batch(cfg, "base", DEV_SPLIT, SCALE_START + (seed % 1000) * batch, batch)
    vals = []
    for i in range(cfg.n):
        up, dn = P.copy(), P.copy()
        up[i, 0] = min(1.0, P[i, 0] + h)
        dn[i, 0] = max(0.0, P[i, 0] - h)
        ou, od = simulate(b, up, cfg), simulate(b, dn, cfg)
        lu = (ou.cost - ou.effort).sum(axis=1) - (ou.cost - ou.effort)[:, i]
        ld = (od.cost - od.effort).sum(axis=1) - (od.cost - od.effort)[:, i]
        dh = load(up)[i] - load(dn)[i]
        vals.append(float((lu - ld).mean() / dh))
    return float(np.mean(vals))


def direct_scale() -> dict:
    """Development scale of the direct charge, per skew: mean over calibration seeds."""
    return {str(sk): float(np.mean([marginal_damage(s, sk) for s in CALIB_SEEDS])) for sk in SKEWS}


# ---------------------------------------------------------------- stages

def experiments(which: str) -> list[dict]:
    S = []
    if which == "calib":   # contract anchor, both effort-on cells
        for seed in CALIB_SEEDS:
            for skew in SKEWS:
                for a in ANCHORS:
                    S.append(spec("calib", seed, effort=EFFORT, skew=skew, arm=f"contract_{a}",
                                  kind="contract", anchor=a, split="dev"))
        return S
    if which == "select":
        lock = json.loads(LOCK.read_text()) if LOCK.exists() else None
        if not lock or "anchor" not in lock:
            raise SystemExit("run `calib` then `lock` first")
        for seed in VALID_SEEDS:
            for skew in SKEWS:
                kw = dict(effort=EFFORT, skew=skew, split="dev")
                sc = lock["direct_scale"][str(skew)]
                S.append(spec("select", seed, arm="private", **kw))
                S.append(spec("select", seed, arm="kantian", kappa=1.0, **kw))
                for lev in GRID:
                    S.append({**spec("select", seed, arm=f"pool_{lev}", kind="pool", level=lev, **kw)})
                    S.append({**spec("select", seed, arm=f"ambient_{lev}", kind="ambient", level=lev, **kw)})
                    S.append({**spec("select", seed, arm=f"direct_{lev}", kind="direct", level=lev, **kw),
                              "scale": sc})
                    if skew:
                        S.append({**spec("select", seed, arm=f"directrole_{lev}", kind="direct",
                                         level=lev, role=True, **kw), "scale": sc})
                S.append(spec("select", seed, arm="contract", kind="contract",
                              anchor=lock["anchor"], **kw))
        return S
    if which in ("E13", "E13sens"):
        lock = json.loads(LOCK.read_text())
        if "selected" not in lock:
            raise SystemExit("selection is not locked")
        for seed in CONFIRM_SEEDS:
            for effort in (0.0, EFFORT):
                for skew in SKEWS:
                    kw = dict(effort=effort, skew=skew)
                    if which == "E13":
                        S.append(spec("E13", seed, arm="private", **kw))
                        S.append(spec("E13", seed, arm="kantian", kappa=1.0, **kw))
                        S.append(spec("E13", seed, arm="pool_1.0", kind="pool", **kw))
                        S.append(spec("E13", seed, arm="ambient_1.0", kind="ambient", **kw))
                    if not effort:
                        continue
                    sel = lock["selected"][str(skew)]
                    strict = {**sel["strict"]["spec"]}
                    amb = {**sel["ambient"]["spec"]}
                    if which == "E13":
                        if strict["arm"] != "pool_1.0":
                            S.append(spec("E13", seed, **kw, **_armkw(strict)))
                        if amb["arm"] != "ambient_1.0":
                            S.append(spec("E13", seed, **kw, **_armkw(amb)))
                        continue
                    # sensitivities, labelled and outside primary inference
                    S.append(spec("E13sens", seed, arm="kantian_noise", kappa=1.0, noise=NOISE_SD, **kw))
                    if strict["kind"] in ("direct", "contract"):
                        S.append({**spec("E13sens", seed, **kw, **_armkw(strict, "_noise")),
                                  "noise": NOISE_SD})
                    S.append({**spec("E13sens", seed, **kw, **_armkw(strict, "_cap")), "capped": True})
                    S.append(spec("E13sens", seed, arm="kantian_bigM", kappa=1.0,
                                  M=lock["big_M"], **kw))
        return S
    raise SystemExit(f"unknown stage {which}")


def _armkw(s: dict, suffix: str = "") -> dict:
    out = dict(arm=s["arm"] + suffix, kind=s["kind"], level=s["level"], role=s["role"],
               anchor=s["anchor"])
    return out


def _with_scale(sp: dict) -> dict:
    """Attach the locked direct-charge scale to confirmatory direct specs."""
    if sp["kind"] == "direct" and "scale" not in sp:
        lock = json.loads(LOCK.read_text())
        sp = {**sp, "scale": lock["direct_scale"][str(sp["skew"])]}
    return sp


# ---------------------------------------------------------------- lock

def lock() -> dict:
    """Write runs/e13_lock.json: calibration results, then (once select ran) the selection.

    Anchor: the lower mean dev-evaluation cost over both effort-on cells, ties to
    'zero'. Selection per effort-on cell: the minimum mean validation cost among
    strict-budget arms (pool, direct, directrole, contract) and among ambient arms,
    ties broken by manifest order (the order of ``experiments('select')``).
    """
    out = json.loads(LOCK.read_text()) if LOCK.exists() else {}
    if "anchor" not in out:
        recs = [json.loads(x) for x in Path("runs/e13_calib.jsonl").read_text().splitlines()]
        means = {a: float(np.mean([score(r) for r in recs if r["anchor"] == a])) for a in ANCHORS}
        out["anchor_means"] = means
        out["anchor"] = min(ANCHORS, key=lambda a: (means[a], list(ANCHORS).index(a)))
        out["direct_scale"] = direct_scale()
        LOCK.write_text(json.dumps(out, indent=1))
        return out
    recs = [json.loads(x) for x in Path("runs/e13_select.jsonl").read_text().splitlines()]
    order = [(s["skew"], s["arm"]) for s in experiments("select") if s["seed"] == VALID_SEEDS[0]]
    sel, contract_sims = {}, []
    for skew in SKEWS:
        rows = {}
        for r in recs:
            if r["skew"] == skew:
                rows.setdefault(r["arm"], []).append(r)
        assert all(len(v) == len(VALID_SEEDS) for v in rows.values()), "incomplete selection runs"
        means = {a: float(np.mean([score(r) for r in v])) for a, v in rows.items()}
        arms = [a for sk, a in order if sk == skew]
        strict = [a for a in arms if a.split("_")[0] in ("pool", "direct", "directrole", "contract")]
        amb = [a for a in arms if a.startswith("ambient_")]
        pick = lambda cands: min(cands, key=lambda a: (means[a], arms.index(a)))
        s_arm, a_arm = pick(strict), pick(amb)
        gate = {r["seed"]: score(r) for r in rows["kantian"]}
        width = {}
        for name, arm in (("strict", s_arm), ("ambient", a_arm)):
            d = np.array([score(r) - gate[r["seed"]] for r in rows[arm]])
            width[name] = float(stats.t.ppf(1 - 0.0125 / 2, len(d) - 1) * d.std(ddof=1) / np.sqrt(len(d)))
        keep = ("arm", "kind", "level", "role", "anchor")
        sel[str(skew)] = {
            "means": means,
            "strict": {"spec": {k: rows[s_arm][0][k] for k in keep}, "mean": means[s_arm],
                       "edge": s_arm.endswith(f"_{GRID[-1]}") or s_arm.endswith(f"_{GRID[0]}")},
            "ambient": {"spec": {k: rows[a_arm][0][k] for k in keep}, "mean": means[a_arm],
                        "edge": a_arm.endswith(f"_{GRID[-1]}") or a_arm.endswith(f"_{GRID[0]}")},
            "expected_halfwidth": width}
        contract_sims += [r["total_sims"] for r in rows["contract"]]
    out["selected"] = sel
    # compute-matched sensitivity: largest M with 40*2M*(1+6*4) <= the contract's median total
    out["contract_total_sims_median"] = float(np.median(contract_sims))
    out["big_M"] = int(out["contract_total_sims_median"] // (GENERATIONS * 2 * 25))
    LOCK.write_text(json.dumps(out, indent=1))
    return out


# ---------------------------------------------------------------- main

def _run(sp):
    return run_one(_with_scale(sp))


def main(argv=None):
    argv = argv or sys.argv[1:]
    Path("runs").mkdir(exist_ok=True)
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True,
                                text=True).stdout.strip()
        dirty = bool(subprocess.run(["git", "status", "--porcelain", "src"],
                                    capture_output=True, text=True).stdout.strip())
    except OSError:
        commit, dirty = "", True
    for which in argv:
        if which == "lock":
            print(json.dumps(lock(), indent=1))
            continue
        specs = experiments(which)
        path = Path("runs") / f"e13_{which}.jsonl" if which in ("calib", "select") else \
            Path("runs") / f"{which}.jsonl"
        t0 = time.time()
        workers = int(os.environ.get("EVO_WORKERS", "0")) or None
        with mp.Pool(workers) as pool, path.open("w", encoding="utf-8") as f:
            for i, rec in enumerate(pool.imap_unordered(_run, specs), 1):
                rec["commit"], rec["dirty"] = commit, dirty
                f.write(json.dumps(rec) + "\n")
                f.flush()
                if i % 20 == 0 or i == len(specs):
                    print(f"{which}: {i}/{len(specs)} runs, {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
