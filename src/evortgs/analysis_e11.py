"""Pre-registered analysis of runs/E11.jsonl (with runs/E10.jsonl) -> runs/results_e11.json.

Written before any E11 run; see docs/PREREGISTRATION_E11.md. E11 re-runs the
Kantian gates (kappa 0.5 and 1) with the universalized counterfactual taken on
three other scales. The linear gates, the ambient tax, the private gate and
the optimum are the E10 records for the same seeds and scenarios.
"""

from __future__ import annotations

import json

import numpy as np

from .analysis import RUNS, boot_mean, paired
from .analysis_e10 import dev, hold, load, spread
from .cb_experiments import E10_SKEWS, E11_SCALES

MARGIN = 0.002
KAPPAS = (0.5, 1.0)


def load_e11():
    out = {}
    for line in (RUNS / "E11.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        out.setdefault((r["skew"], f"k{r['kappa']:g}@{r['scale']}"), {})[r["seed"]] = r
    return out


def main():
    E10, E11 = load(), load_e11()
    res = {"n_runs_e11": sum(len(v) for v in E11.values()), "margin": MARGIN, "skews": {}}
    for skew in E10_SKEWS:
        cells = {f"k{k:g}@linear": E10[(skew, f"k{k:g}")] for k in KAPPAS}
        cells.update({lab: c for (s, lab), c in E11.items() if s == skew})
        cells["k0"] = E10[(skew, "k0")]
        amb, opt = E10[(skew, "ambient1")], E10[(skew, "planner_asym")]
        R = {"arms": {}, "tests": {}}
        for lab, c in sorted(cells.items()):
            R["arms"][lab] = {"cost": boot_mean(hold(c)), "dev_cost": dev(c),
                              "s_by_agent": np.mean([np.asarray(c[s]["profile"]) for s in c],
                                                    axis=0)[:, 0].round(4).tolist()}
        R["arms"]["ambient1"] = {"cost": boot_mean(hold(amb)), "dev_cost": dev(amb)}
        R["arms"]["optimum"] = {"cost": boot_mean(hold(opt))}
        best = min(cells, key=lambda lab: dev(cells[lab]))
        R["best_own_cost_gate_all_scales"] = best
        T = R["tests"]
        T["U1_ambient_vs_best_gate"] = paired(hold(amb), hold(cells[best]))
        for lab in cells:
            if lab.startswith("k1@") and lab != "k1@linear":
                T[f"U2_{lab}_vs_linear"] = paired(hold(cells[lab]), hold(cells["k1@linear"]))
            if lab.startswith("k1@"):
                T[f"U3_spread_{lab}_minus_optimum"] = boot_mean(spread(cells[lab]) - spread(opt))
                T[f"ambient_vs_{lab}"] = paired(hold(amb), hold(cells[lab]))
        d = T["U1_ambient_vs_best_gate"]["diff"]
        R["verdicts"] = {
            "ambient_clearly_cheaper": d[2] < 0,
            "gate_clearly_cheaper_beyond_margin": d[1] > 0 and -d[0] > MARGIN,
            "within_margin": -MARGIN < d[1] and d[2] < MARGIN,
        }
        if skew == 0.0:
            R["verdicts"]["U4_k1_scales_equivalent_at_skew0"] = all(
                -MARGIN < T[k]["diff"][1] and T[k]["diff"][2] < MARGIN
                for k in T if k.startswith("U2_"))
        res["skews"][f"{skew:g}"] = R
    het = [f"{s:g}" for s in E10_SKEWS if s > 0]
    res["strong_line_reopens"] = all(
        res["skews"][k]["verdicts"]["gate_clearly_cheaper_beyond_margin"] for k in het)
    res["e10_closure_robust"] = all(res["skews"][k]["verdicts"]["ambient_clearly_cheaper"]
                                    for k in het)
    (RUNS / "results_e11.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    figure(res)
    for k, R in res["skews"].items():
        print(k, R["best_own_cost_gate_all_scales"], json.dumps(R["verdicts"]))
    print("strong line reopens:", res["strong_line_reopens"],
          "| E10 closure robust to scale:", res["e10_closure_robust"])


def figure(res):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(7, 4))
    xs = np.arange(len(E10_SKEWS))
    series = [(f"k1@{s}", f"Kantian gate, {s} scale") for s in ("linear",) + E11_SCALES]
    series += [("ambient1", "ambient tax"), ("optimum", "optimum")]
    colors = ["#2a5d8f", "#5b8fc2", "#8fb4d9", "#b9cfe6", "#c0602a", "#000000"]
    for j, (lab, name) in enumerate(series):
        ys = [res["skews"][f"{s:g}"]["arms"][lab]["cost"] for s in E10_SKEWS]
        ax.errorbar(xs + (j - 2.5) * 0.07, [y[0] for y in ys],
                    yerr=[[y[0] - y[1] for y in ys], [y[2] - y[0] for y in ys]],
                    fmt="o", color=colors[j], label=name, capsize=2)
    ax.set_xticks(xs, [f"{s:g}" for s in E10_SKEWS])
    ax.set_xlabel("exposure skew")
    ax.set_ylabel("holdout system cost (lower is better)")
    ax.legend(fontsize=7)
    ax.grid(axis="y", alpha=0.3)
    fig.tight_layout()
    fig.savefig(RUNS / "fig_e11.png", dpi=150)


if __name__ == "__main__":
    main()
