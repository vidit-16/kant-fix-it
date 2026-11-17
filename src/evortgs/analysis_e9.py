"""Pre-registered analysis of runs/E9.jsonl -> runs/results_e9.json, runs/fig_e9.png.

Written and committed before any E9 run; see docs/PREREGISTRATION_E9.md.
"""

from __future__ import annotations

import json
from collections import defaultdict

import numpy as np

from .analysis import RUNS, boot_mean, paired
from .cb_experiments import E9_GRIDS
from .codebase import FAMILIES

MARGIN = 0.002            # equivalence margin on holdout cost (about 1 % of planner cost)
BALANCED = ("proxy", "activity", "surface")   # instruments that need not break the budget
REGIMES = [(g, n) for g in (0.25, 1.0) for n in (6, 12)]


def label(r):
    if r["kind"] == "planner":
        return "planner"
    if r["instrument"]:
        return f"{r['instrument']}{r['level']:g}"
    if r["gate"] == "kappa":
        return f"k{r['kappa']:g}"
    return r["gate"]


def load(name="E9"):
    out = defaultdict(dict)
    for line in (RUNS / f"{name}.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        out[(r["gamma"], r["n"], label(r))][r["seed"]] = r
    return out


def hold(cell, key="system_cost"):
    return np.array([np.mean([cell[s]["eval"][f][key] for f in FAMILIES]) for s in sorted(cell)])


def dev(cell):
    return float(np.mean([cell[s]["history"][-1]["dev_system_cost"] for s in sorted(cell)]))


def clearly_pos(p):
    return p["diff"][1] > 0


def clearly_neg(p):
    return p["diff"][2] < 0


def within_margin(p):
    return -MARGIN < p["diff"][1] and p["diff"][2] < MARGIN


def main():
    E = load()
    res = {"n_runs": sum(len(v) for v in E.values()), "margin": MARGIN, "regimes": {}}
    for gamma, n in REGIMES:
        key = f"gamma={gamma:g},n={n}"
        cell = lambda lab: E[(gamma, n, lab)]
        R = {"choice": {}, "arms": {}}
        insts = [i for i in E9_GRIDS if (gamma, n, f"{i}{E9_GRIDS[i][0]:g}") in E]
        chosen = {}
        for inst in insts:
            d = {lev: dev(cell(f"{inst}{lev:g}")) for lev in E9_GRIDS[inst]}
            best = min(d, key=d.get)
            chosen[inst] = f"{inst}{best:g}"
            R["choice"][inst] = {"dev_cost_last_gen": {f"{k:g}": v for k, v in d.items()},
                                 "chosen": best,
                                 "holdout_by_level": {f"{k:g}": float(hold(cell(f"{inst}{k:g}")).mean())
                                                      for k in E9_GRIDS[inst]}}
        best_inst = min(chosen.values(), key=lambda lab: dev(cell(lab)))
        bal = [chosen[i] for i in BALANCED if i in chosen]
        best_bal = min(bal, key=lambda lab: dev(cell(lab)))
        best_gate = min(("k0", "k1"), key=lambda lab: dev(cell(lab)))
        R["choice"].update({"best_instrument": best_inst, "best_balanced": best_bal,
                            "best_own_cost_gate": best_gate})
        labels = sorted({lab for (g, m, lab) in E if (g, m) == (gamma, n)})
        for lab in labels:
            c = cell(lab)
            R["arms"][lab] = {"cost": boot_mean(hold(c)),
                              "hidden_share": float(hold(c, "hidden_share").mean()),
                              "incidents": float(hold(c, "incidents").mean()),
                              "policy_mean": np.mean([c[s]["eval"]["policy_mean"] for s in c],
                                                     axis=0).tolist(),
                              "dev_cost": dev(c) if lab != "planner" else None}
        v = lambda lab: hold(cell(lab))
        H = {}
        H["C1_k0_vs_planner"] = paired(v("k0"), v("planner"))
        gap = v("k0") - v("planner")
        clos = (v("k0") - v("k1")) / gap
        H["C2_k1_closure"] = boot_mean(clos) if gap.min() > 0 else None
        H["C2_k1_closure_ratio_of_means"] = float((v("k0") - v("k1")).mean() / gap.mean())
        H["C3C4_proxy_vs_gate"] = paired(v(chosen["proxy"]), v(best_gate))
        H["C4_hidden_share_proxy_ge_0.2"] = float(np.mean(
            [hold(cell(f"proxy{lev:g}"), "hidden_share").mean() for lev in (0.2, 0.4, 0.8)]))
        H["C5_best_instrument_vs_gate"] = paired(v(best_inst), v(best_gate))
        H["C5_ambient_vs_gate"] = paired(v(chosen["ambient"]), v(best_gate))
        H["C5b_best_balanced_vs_gate"] = paired(v(best_bal), v(best_gate))
        H["k1_vs_planner"] = paired(v("k1"), v("planner"))
        H["welfare_vs_k1"] = paired(v("welfare"), v("k1"))
        if (gamma, n, "welfare_universal") in E:
            H["welfare_universal_vs_k1"] = paired(v("welfare_universal"), v("k1"))
        same = all(cell("ambient1")[s]["profile"] == cell("welfare")[s]["profile"]
                   for s in cell("welfare"))
        H["identity_ambient1_equals_welfare_gate"] = same
        if "activity" in chosen:
            H["activity_identical_to_k0_profiles"] = all(
                cell(f"activity{lev:g}")[s]["profile"] == cell("k0")[s]["profile"]
                for lev in E9_GRIDS["activity"] for s in cell("k0"))
        R["tests"] = H
        R["verdicts"] = {
            "C1": clearly_pos(H["C1_k0_vs_planner"]),
            "C2": H["C2_k1_closure_ratio_of_means"] >= 0.8,
            "C5_gate_clearly_cheaper_than_best_instrument": clearly_pos(H["C5_best_instrument_vs_gate"]),
            "C5_equivalent_within_margin": within_margin(H["C5_best_instrument_vs_gate"]),
            "C5b_gate_clearly_cheaper_than_best_balanced": clearly_pos(H["C5b_best_balanced_vs_gate"]),
        }
        if gamma == 1.0:
            R["verdicts"]["C3_proxy_not_clearly_worse"] = not clearly_pos(H["C3C4_proxy_vs_gate"])
        else:
            R["verdicts"]["C4_proxy_clearly_worse_and_concealed"] = (
                clearly_pos(H["C3C4_proxy_vs_gate"]) and H["C4_hidden_share_proxy_ge_0.2"] > 0.5)
        res["regimes"][key] = R

    # C7: does the ambient tax lose ground to the gate as n grows?
    c7 = {}
    for gamma in (0.25, 1.0):
        def gapv(n):
            amb = res["regimes"][f"gamma={gamma:g},n={n}"]["choice"]["ambient"]["chosen"]
            gate = res["regimes"][f"gamma={gamma:g},n={n}"]["choice"]["best_own_cost_gate"]
            return hold(E[(gamma, n, f"ambient{amb:g}")]) - hold(E[(gamma, n, gate)])
        c7[f"gamma={gamma:g}"] = paired(gapv(12), gapv(6))
    res["C7_n_interaction"] = c7

    # Kill criterion, primary regime first (gamma = 0.25, n = 6), then all regimes.
    prim = res["regimes"]["gamma=0.25,n=6"]["verdicts"]
    res["kill_criterion_fires"] = not prim["C5_gate_clearly_cheaper_than_best_instrument"]
    res["kill_by_regime"] = {k: not R["verdicts"]["C5_gate_clearly_cheaper_than_best_instrument"]
                             for k, R in res["regimes"].items()}
    (RUNS / "results_e9.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    figure(res)
    print(json.dumps({k: R["verdicts"] for k, R in res["regimes"].items()}, indent=1))
    print("kill criterion fires (primary regime):", res["kill_criterion_fires"])


def figure(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharey=True)
    for ax, gamma in zip(axes, (0.25, 1.0)):
        R = res["regimes"][f"gamma={gamma:g},n=6"]
        ch = R["choice"]
        arms = [("private gate", "k0"), ("Kantian gate", "k1"), ("welfare gate", "welfare"),
                ("proxy charge*", f"proxy{ch['proxy']['chosen']:g}"),
                ("surface charge*", f"surface{ch['surface']['chosen']:g}"),
                ("ambient tax*", f"ambient{ch['ambient']['chosen']:g}"),
                ("optimum (grid)", "planner")]
        ys = [R["arms"][lab]["cost"] for _, lab in arms]
        x = np.arange(len(arms))
        ax.errorbar(x, [y[0] for y in ys], yerr=[[y[0] - y[1] for y in ys], [y[2] - y[0] for y in ys]],
                    fmt="o", color="#2a5d8f", capsize=3)
        ax.axhline(ys[-1][0], color="#888888", lw=0.8, ls="--")
        ax.set_xticks(x, [a for a, _ in arms], rotation=35, ha="right", fontsize=8)
        ax.set_title(f"concealment cost gamma = {gamma:g} (six agents)", fontsize=9)
        ax.grid(axis="y", alpha=0.3)
    axes[0].set_ylabel("holdout system cost (lower is better)")
    fig.tight_layout()
    fig.savefig(RUNS / "fig_e9.png", dpi=150)


if __name__ == "__main__":
    main()
