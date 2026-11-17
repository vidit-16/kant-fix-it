"""Pre-registered analysis of runs/E10.jsonl -> runs/results_e10.json, runs/fig_e10.png.

Written and committed before any E10 run; see docs/PREREGISTRATION_E10.md.
"""

from __future__ import annotations

import json
from collections import defaultdict

import numpy as np

from .analysis import RUNS, boot_mean, paired
from .cb_experiments import E10_GRIDS, E10_SKEWS
from .codebase import FAMILIES

MARGIN = 0.002
BALANCED = ("proxy", "surface")
GATES = ("k0", "k0.5", "k1")


def label(r):
    if r["kind"] in ("planner", "planner_asym"):
        return r["kind"]
    if r["instrument"]:
        return f"{r['instrument']}{r['level']:g}"
    if r["gate"] == "kappa":
        return f"k{r['kappa']:g}"
    return r["gate"]


def load(name="E10"):
    out = defaultdict(dict)
    for line in (RUNS / f"{name}.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        out[(r.get("skew", 0.0), label(r))][r["seed"]] = r
    return out


def hold(cell, key="system_cost"):
    return np.array([np.mean([cell[s]["eval"][f][key] for f in FAMILIES]) for s in sorted(cell)])


def dev(cell):
    return float(np.mean([cell[s]["history"][-1]["dev_system_cost"] for s in sorted(cell)]))


def spread(cell):
    """Per seed: shortcut intensity of the least exposed agent minus the most exposed."""
    return np.array([cell[s]["profile"][-1][0] - cell[s]["profile"][0][0] for s in sorted(cell)])


def main():
    E = load()
    res = {"n_runs": sum(len(v) for v in E.values()), "margin": MARGIN, "skews": {}}
    closure = {}
    for skew in E10_SKEWS:
        cell = lambda lab: E[(skew, lab)]
        v = lambda lab: hold(cell(lab))
        R = {"choice": {}, "arms": {}, "tests": {}}
        chosen = {}
        for inst, levels in E10_GRIDS.items():
            d = {lev: dev(cell(f"{inst}{lev:g}")) for lev in levels}
            best = min(d, key=d.get)
            chosen[inst] = f"{inst}{best:g}"
            R["choice"][inst] = {"dev_cost_last_gen": {f"{k:g}": x for k, x in d.items()},
                                 "chosen": best,
                                 "holdout_by_level": {f"{k:g}": float(v(f"{inst}{k:g}").mean())
                                                      for k in levels}}
        best_inst = min(chosen.values(), key=lambda lab: dev(cell(lab)))
        best_bal = min((chosen[i] for i in BALANCED), key=lambda lab: dev(cell(lab)))
        best_gate = min(GATES, key=lambda lab: dev(cell(lab)))
        R["choice"].update({"best_instrument": best_inst, "best_balanced": best_bal,
                            "best_own_cost_gate": best_gate})
        for lab in sorted({lab for (s, lab) in E if s == skew}):
            c = cell(lab)
            P = np.mean([np.asarray(c[s]["profile"]) for s in c], axis=0)
            R["arms"][lab] = {"cost": boot_mean(hold(c)),
                              "s_by_agent": P[:, 0].round(4).tolist(),
                              "q_by_agent": P[:, 2].round(4).tolist(),
                              "hidden_share": float(hold(c, "hidden_share").mean()),
                              "dev_cost": None if lab.startswith("planner") else dev(c)}
        T = R["tests"]
        ref = v("planner_asym")
        T["D1_k0_vs_optimum"] = paired(v("k0"), ref)
        T["D2_best_instrument_vs_gate"] = paired(v(best_inst), v(best_gate))
        T["D2_ambient_vs_gate"] = paired(v(chosen["ambient"]), v(best_gate))
        T["D5_best_balanced_vs_gate"] = paired(v(best_bal), v(best_gate))
        T["k1_vs_optimum"] = paired(v("k1"), ref)
        T["ambient_vs_optimum"] = paired(v(chosen["ambient"]), ref)
        T["symmetric_planner_vs_optimum"] = paired(v("planner"), ref)
        gap = v("k0") - ref
        closure[skew] = (v("k0") - v("k1")) / gap
        T["k1_closure"] = boot_mean(closure[skew])
        T["k1_closure_ratio_of_means"] = float((v("k0") - v("k1")).mean() / gap.mean())
        T["D4_spread_k1_minus_optimum"] = boot_mean(spread(cell("k1")) - spread(cell("planner_asym")))
        T["D4_spread_ambient_minus_optimum"] = boot_mean(
            spread(cell(chosen["ambient"])) - spread(cell("planner_asym")))
        T["D6_identity_ambient1_equals_welfare"] = all(
            cell("ambient1")[s]["profile"] == cell("welfare")[s]["profile"] for s in cell("welfare"))
        d2 = T["D2_best_instrument_vs_gate"]["diff"]
        R["verdicts"] = {
            "D1_dilemma": T["D1_k0_vs_optimum"]["diff"][1] > 0,
            "D2_instrument_clearly_cheaper": d2[2] < 0,
            "gate_survives_rule": d2[1] > 0 and d2[0] > MARGIN,
            "within_margin": -MARGIN < d2[1] and d2[2] < MARGIN,
            "D5_gate_clearly_cheaper_than_balanced": T["D5_best_balanced_vs_gate"]["diff"][1] > 0,
        }
        res["skews"][f"{skew:g}"] = R
    res["D3_closure_change"] = {f"{s:g}": boot_mean(closure[s] - closure[0.0])
                                for s in E10_SKEWS if s > 0}
    res["D4_verdict_skew1.5"] = res["skews"]["1.5"]["tests"]["D4_spread_k1_minus_optimum"][1] > 0
    res["D3_verdict_skew1.5"] = res["D3_closure_change"]["1.5"][2] < 0
    het = [f"{s:g}" for s in E10_SKEWS if s > 0]
    res["strong_line_survives"] = all(res["skews"][k]["verdicts"]["gate_survives_rule"] for k in het)
    (RUNS / "results_e10.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    figure(res)
    print(json.dumps({k: R["verdicts"] for k, R in res["skews"].items()}, indent=1))
    print("D3 closure falls (skew 1.5):", res["D3_verdict_skew1.5"],
          "| D4 Kantian spread distortion (skew 1.5):", res["D4_verdict_skew1.5"])
    print("strong line survives:", res["strong_line_survives"])


def figure(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    arms = [("private gate", "k0"), ("Kantian gate", "k1"), ("ambient tax*", None),
            ("best budget-balanced*", None), ("optimum", "planner_asym")]
    colors = ["#888888", "#2a5d8f", "#c0602a", "#7a9a3a", "#000000"]
    xs = np.arange(len(E10_SKEWS))
    for j, (name, lab) in enumerate(arms):
        ys = []
        for skew in E10_SKEWS:
            R = res["skews"][f"{skew:g}"]
            key = lab or (f"ambient{R['choice']['ambient']['chosen']:g}" if "ambient" in name
                          else R["choice"]["best_balanced"])
            ys.append(R["arms"][key]["cost"])
        axes[0].errorbar(xs + (j - 2) * 0.08, [y[0] for y in ys],
                         yerr=[[y[0] - y[1] for y in ys], [y[2] - y[0] for y in ys]],
                         fmt="o", color=colors[j], label=name, capsize=2)
    axes[0].set_xticks(xs, [f"{s:g}" for s in E10_SKEWS])
    axes[0].set_xlabel("exposure skew")
    axes[0].set_ylabel("holdout system cost (lower is better)")
    axes[0].legend(fontsize=7)
    axes[0].grid(axis="y", alpha=0.3)
    R = res["skews"]["1.5"]
    amb = f"ambient{R['choice']['ambient']['chosen']:g}"
    for lab, name, c in (("planner_asym", "optimum", "#000000"), ("k1", "Kantian gate", "#2a5d8f"),
                         (amb, "ambient tax*", "#c0602a")):
        axes[1].plot(range(1, 7), R["arms"][lab]["s_by_agent"], "o-", color=c, label=name)
    axes[1].set_xlabel("agent, most exposed (1) to least exposed (6)")
    axes[1].set_ylabel("shortcut intensity s (seed mean)")
    axes[1].set_title("exposure skew 1.5", fontsize=9)
    axes[1].legend(fontsize=7)
    axes[1].grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(RUNS / "fig_e10.png", dpi=150)


if __name__ == "__main__":
    main()
