"""Pre-registered analysis of runs/E*.jsonl -> runs/results.json, RESULTS.md, figures."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

import numpy as np
from scipy import stats

from .scenarios import FAMILIES

RUNS = Path("runs")
RNG = np.random.default_rng(20261117)
B = 10_000


def label(r):
    if r["kind"] == "planner":
        return "planner"
    if r["gate"] != "kappa":
        return r["gate"]
    lab = f"k{r['kappa']:g}"
    return lab + (f"+fee{r['fee']:g}" if r["fee"] else "")


def load(name):
    out = defaultdict(dict)  # (exp, d, n, het, label) -> seed -> record
    for line in (RUNS / f"{name}.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        out[(r["exp"], r["delay_day"], r["n"], r["het"], label(r))][r["seed"]] = r
    return out


def cost(r, fam=None):
    if fam:
        return r["eval"][fam]["system_cost"]
    return float(np.mean([r["eval"][f]["system_cost"] for f in FAMILIES]))


def vec(cell, fam=None, key=None):
    seeds = sorted(cell)
    if key:
        return np.array([np.mean([cell[s]["eval"][f][key] for f in FAMILIES]) for s in seeds])
    return np.array([cost(cell[s], fam) for s in seeds])


def boot_mean(x):
    idx = RNG.integers(0, len(x), size=(B, len(x)))
    m = x[idx].mean(axis=1)
    return [float(x.mean()), float(np.percentile(m, 2.5)), float(np.percentile(m, 97.5))]


def paired(a, b):
    """a - b, seed-paired."""
    d = a - b
    p = float(stats.wilcoxon(d).pvalue) if np.any(d != 0) else 1.0
    return {"diff": boot_mean(d), "p": p, "dz": float(d.mean() / d.std(ddof=1)),
            "rel": float(d.mean() / b.mean())}


def gap_closure(k0, g, ref):
    idx = RNG.integers(0, len(k0), size=(B, len(k0)))
    num = (k0 - g)[idx].mean(axis=1)
    den = (k0 - ref)[idx].mean(axis=1)
    gc = num / den
    point = float((k0 - g).mean() / (k0 - ref).mean())
    return [point, float(np.percentile(gc, 2.5)), float(np.percentile(gc, 97.5))], gc


def holm(ps):
    order = np.argsort(ps)
    adj = np.empty(len(ps))
    run = 0.0
    for rank, i in enumerate(order):
        run = max(run, (len(ps) - rank) * ps[i])
        adj[i] = min(1.0, run)
    return adj.tolist()


def main():
    E1, E2, E3, E4, E5, E6 = (load(e) for e in ("E1", "E2", "E3", "E4", "E5", "E6"))
    res = {}
    base = ("E1", 0.5, 6, 0.0)
    c = {lab: vec(E1[base + (lab,)]) for (_e, _d, _n, _h, lab) in E1}

    # invariants: evaluate() runs with check=True and would have raised
    res["n_runs"] = sum(len(v) for E in (E1, E2, E3, E4, E5, E6) for v in E.values())

    # arm table
    arms = {}
    for lab in sorted(c):
        cell = E1[base + (lab,)]
        arms[lab] = {"cost": boot_mean(c[lab]),
                     "unsettled": float(vec(cell, key="unsettled").mean()),
                     "delay_ticks": float(vec(cell, key="delay_ticks").mean()),
                     "liquidity": float(vec(cell, key="liquidity").mean()),
                     "vs_k0": paired(c[lab], c["k0"]) if lab != "k0" else None}
    res["E1_arms"] = arms

    res["H1"] = paired(c["k0"], c["planner"])
    gc1, gc1_samples = gap_closure(c["k0"], c["k1"], c["planner"])
    res["H2_gap_closure_k1"] = gc1
    kl = [0.0, 0.25, 0.5, 0.75, 1.0]
    M = np.stack([c[f"k{k:g}"] for k in kl], axis=1)  # seeds x kappa
    rho = []
    for _ in range(B):
        m = M[RNG.integers(0, len(M), len(M))]
        rho.append(stats.spearmanr(np.tile(kl, len(m)), m.ravel())[0])
    res["H2b_spearman"] = [float(stats.spearmanr(np.tile(kl, len(M)), M.ravel())[0]),
                           float(np.percentile(rho, 2.5)), float(np.percentile(rho, 97.5))]
    res["H2b_means"] = {f"k{k:g}": float(M[:, i].mean()) for i, k in enumerate(kl)}

    # H3 heterogeneity
    h3 = {"0": gc1}
    samples = {"0": gc1_samples}
    worse = {}
    for het, E, key in ((0.0, E1, base), (0.75, E2, ("E2", 0.5, 6, 0.75)), (1.5, E2, ("E2", 0.5, 6, 1.5))):
        k0c, k1c, pl = E[key + ("k0",)], E[key + ("k1",)], E[key + ("planner",)]
        if het:
            h3[str(het)], samples[str(het)] = gap_closure(vec(k0c), vec(k1c), vec(pl))
        seeds = sorted(k0c)
        bank = lambda cell: np.array([np.mean([cell[s]["eval"][f]["bank_cost"] for f in FAMILIES], axis=0) for s in seeds])
        d = (bank(k1c) - bank(k0c)).mean(axis=0)
        worse[str(het)] = {"banks_worse_under_k1": int((d > 0).sum()),
                           "mean_change_by_bank_rank": d.round(4).tolist(),
                           "arms": {lab: boot_mean(vec(E[key + (lab,)]))
                                    for lab in ("k0", "k1", "welfare", "welfare_universal", "noharm", "planner")}}
    dd = samples["0"] - samples["1.5"]
    res["H3"] = {"gap_closure": h3, "diff_0_minus_1.5": [float(h3["0"][0] - h3["1.5"][0]),
                 float(np.percentile(dd, 2.5)), float(np.percentile(dd, 97.5))], "detail": worse}

    # H4 per family
    k0c, k1c = E1[base + ("k0",)], E1[base + ("k1",)]
    fam = {f: paired(vec(k1c, f), vec(k0c, f)) for f in FAMILIES}
    adj = holm([fam[f]["p"] for f in FAMILIES])
    for f, a in zip(FAMILIES, adj):
        fam[f]["p_holm"] = a
    res["H4"] = fam

    # H5 defector
    h5 = {}
    for het, E, key in ((0.0, E1, base), (1.5, E2, ("E2", 0.5, 6, 1.5))):
        mixed, allk = E4[("E4", 0.5, 6, het, "k1")], E[key + ("k1",)]
        seeds = sorted(mixed)
        own = lambda cell, s: np.mean([cell[s]["eval"][f]["bank_cost"][s % 6] for f in FAMILIES])
        a = np.array([own(mixed, s) for s in seeds])
        b = np.array([own(allk, s) for s in seeds])
        h5[str(het)] = {"defector_own_cost": paired(a, b),
                        "system_cost": paired(vec(mixed), vec(allk))}
    res["H5"] = h5

    res["H6"] = {"k1_vs_welfare": paired(c["k1"], c["welfare"]),
                 "k1_vs_welfare_universal": paired(c["k1"], c["welfare_universal"]),
                 "noharm_vs_k1": paired(c["noharm"], c["k1"])}

    # fee baseline chosen on development cost
    dev = {}
    for fee in (1, 2, 4, 8):
        cell = E1[base + (f"k0+fee{fee}",)]
        dev[fee] = float(np.mean([cell[s]["history"][-1]["dev_system_cost"] for s in cell]))
    best = min(dev, key=dev.get)
    res["fee"] = {"dev_cost_last_gen": dev, "chosen": best,
                  "chosen_vs_k0": paired(c[f"k0+fee{best}"], c["k0"]),
                  "chosen_vs_k1": paired(c[f"k0+fee{best}"], c["k1"]),
                  "chosen_vs_noharm": paired(c[f"k0+fee{best}"], c["noharm"]),
                  "chosen_vs_planner": paired(c[f"k0+fee{best}"], c["planner"])}

    res["E3"] = {}
    for d in (0.1, 2.0, 6.0):
        key = ("E3", d, 6, 0.0)
        v = {lab: vec(E3[key + (lab,)]) for lab in ("k0", "k1", "welfare", "planner")}
        res["E3"][str(d)] = {"means": {k: float(x.mean()) for k, x in v.items()},
                             "k0_vs_planner": paired(v["k0"], v["planner"]),
                             "k1_vs_k0": paired(v["k1"], v["k0"]),
                             "gap_closure_k1": gap_closure(v["k0"], v["k1"], v["planner"])[0]}
    res["E5"] = {}
    for name, n in (("E5seq", 6), ("E5n10", 10)):
        key = (name, 0.5, n, 0.0)
        v = {lab: vec(E5[key + (lab,)]) for lab in ("k0", "k1", "welfare")}
        res["E5"][name] = {"means": {k: float(x.mean()) for k, x in v.items()},
                           "k1_vs_k0": paired(v["k1"], v["k0"]),
                           "k1_vs_welfare": paired(v["k1"], v["welfare"])}
    key = ("E6", 0.5, 6, 0.0)
    v = {lab: vec(E6[key + (lab,)]) for lab in ("k0", "k1", "welfare")}
    res["E6"] = {"means": {k: float(x.mean()) for k, x in v.items()},
                 "same_seeds_40gen": {k: float(c[k][:10].mean()) for k in v},
                 "k1_vs_k0": paired(v["k1"], v["k0"]),
                 "k1_vs_welfare": paired(v["k1"], v["welfare"])}

    (RUNS / "results.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    figures(E1, base, c, res)
    print(json.dumps({k: res[k] for k in ("H1", "H2_gap_closure_k1", "H2b_spearman", "H6", "fee")}, indent=1))


def figures(E1, base, c, res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    order = ["k0", "k0.25", "k0.5", "k0.75", "k1", "welfare", "welfare_universal",
             "noharm", "k0+fee1", "k0+fee2", "k0+fee4", "k0+fee8", "planner"]
    fig, ax = plt.subplots(figsize=(9, 4))
    m = [res["E1_arms"][a]["cost"] for a in order]
    ax.bar(range(len(order)), [x[0] for x in m], color="#4c72b0",
           yerr=[[x[0] - x[1] for x in m], [x[2] - x[0] for x in m]], capsize=3)
    ax.set_xticks(range(len(order)), order, rotation=45, ha="right")
    ax.set_ylabel("holdout system cost / payment value")
    ax.set_title("E1: acceptance gates, homogeneous banks (mean, 95% bootstrap CI, 20 seeds)")
    ax.set_ylim(0.5, None)
    fig.tight_layout()
    fig.savefig(RUNS / "fig_gates.png", dpi=150)

    fig, ax = plt.subplots(figsize=(6, 4))
    for lab in ("k0", "k0.5", "k1", "welfare", "noharm", "k0+fee8"):
        cell = E1[base + (lab,)]
        h = np.array([[g["dev_system_cost"] for g in cell[s]["history"]] for s in sorted(cell)])
        ax.plot(h.mean(axis=0) / h[:, :1].mean(), label=lab)
    ax.set_xlabel("generation")
    ax.set_ylabel("development system cost (relative to generation 0)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RUNS / "fig_trajectories.png", dpi=150)


if __name__ == "__main__":
    main()
