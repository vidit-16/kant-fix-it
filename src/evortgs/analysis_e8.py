"""Pre-registered analysis of runs/E8.jsonl -> runs/results_e8.json, runs/fig_e8.png."""

from __future__ import annotations

import json
from collections import defaultdict

import numpy as np

from .analysis import B, RNG, RUNS, boot_mean, paired
from .scenarios import FAMILIES

FEES = (4, 8, 16, 32)
TARS = (0.5, 1, 2, 4)
BOUNDARY = 10  # first tick of the charged band


def label(r):
    if r["kind"] == "planner":
        return "planner"
    if r["gate"] != "kappa":
        return r["gate"]
    if r["fee"]:
        return f"fee{r['fee']:g}"
    if r["tariff"]:
        return f"tar{r['tariff']:g}"
    return f"k{r['kappa']:g}"


def load():
    out = defaultdict(dict)  # (space, label) -> seed -> record
    for line in (RUNS / "E8.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        out[("rich" if r["rich"] else "simple", label(r))][r["seed"]] = r
    return out


def vec(cell, f=None):
    f = f or (lambda e: e["system_cost"])
    return np.array([np.mean([f(cell[s]["eval"][fam]) for fam in FAMILIES]) for s in sorted(cell)])


def interaction(a_rich, a_simple, b_rich, b_simple):
    return paired(a_rich - a_simple, b_rich - b_simple)


def main():
    E = load()
    res = {"n_runs": sum(len(v) for v in E.values())}
    c = {k: vec(v) for k, v in E.items()}
    tick9 = lambda e: e["settle_share"][BOUNDARY - 1]
    chosen = {}
    for space in ("simple", "rich"):
        for name, grid in (("fee", FEES), ("tar", TARS)):
            dev = {g: float(np.mean([r["history"][-1]["dev_system_cost"]
                                     for r in E[(space, f"{name}{g:g}")].values()])) for g in grid}
            best = min(dev, key=dev.get)
            chosen[(space, name)] = f"{name}{best:g}"
            res[f"{name}_choice_{space}"] = {"dev_cost_last_gen": dev, "chosen": best,
                                             "holdout_by_level": {f"{g:g}": float(c[(space, f"{name}{g:g}")].mean())
                                                                  for g in grid}}
        c[(space, "fee*")] = c[(space, chosen[(space, "fee")])]
        c[(space, "tar*")] = c[(space, chosen[(space, "tar")])]

    arms = ("k0", "k1", "welfare", "welfare_universal", "fee*", "tar*", "planner")
    res["arms"] = {}
    for space in ("simple", "rich"):
        for a in arms:
            src = E[(space, chosen.get((space, a[:3]), a) if a.endswith("*") else a)]
            res["arms"][f"{space}/{a}"] = {
                "cost": boot_mean(c[(space, a)]),
                "unsettled": float(vec(src, lambda e: e["unsettled"]).mean()),
                "liquidity": float(vec(src, lambda e: e["liquidity"]).mean()),
                "delay_ticks": float(vec(src, lambda e: e["delay_ticks"]).mean()),
                "tick9_share": float(vec(src, tick9).mean())}

    R, S = "rich", "simple"
    res["R1"] = {"fee_vs_k1": paired(c[(R, "fee*")], c[(R, "k1")]),
                 "fee_vs_welfare_universal": paired(c[(R, "fee*")], c[(R, "welfare_universal")]),
                 "simple_fee_vs_k1": paired(c[(S, "fee*")], c[(S, "k1")]),
                 "simple_fee_vs_welfare_universal": paired(c[(S, "fee*")], c[(S, "welfare_universal")])}
    res["R2"] = {"wu": interaction(c[(R, "welfare_universal")], c[(S, "welfare_universal")],
                                   c[(R, "fee*")], c[(S, "fee*")]),
                 "k1": interaction(c[(R, "k1")], c[(S, "k1")], c[(R, "fee*")], c[(S, "fee*")]),
                 "wu_rich_minus_simple": paired(c[(R, "welfare_universal")], c[(S, "welfare_universal")]),
                 "k1_rich_minus_simple": paired(c[(R, "k1")], c[(S, "k1")])}
    res["R3"] = {"k1_vs_k0": paired(c[(R, "k1")], c[(R, "k0")]),
                 "k1_vs_welfare": paired(c[(R, "k1")], c[(R, "welfare")])}
    t9 = lambda space, name: vec(E[(space, chosen[(space, name)])], tick9)
    res["R4"] = {"interaction": interaction(c[(R, "tar*")], c[(R, "fee*")], c[(S, "tar*")], c[(S, "fee*")]),
                 "tar_vs_fee_rich": paired(c[(R, "tar*")], c[(R, "fee*")]),
                 "tar_vs_fee_simple": paired(c[(S, "tar*")], c[(S, "fee*")]),
                 "tar_vs_k0_rich": paired(c[(R, "tar*")], c[(R, "k0")]),
                 "tick9_tar_vs_fee_rich": paired(t9(R, "tar"), t9(R, "fee")),
                 "tick9_tar_rich_vs_simple": paired(t9(R, "tar"), t9(S, "tar"))}
    res["R5"] = {"k0": paired(c[(R, "k0")], c[(S, "k0")]),
                 "fee": paired(c[(R, "fee*")], c[(S, "fee*")])}
    res["mean_rich_profile"] = {
        a: np.mean([E[(R, chosen.get((R, a[:3]), a) if a.endswith("*") else a)][s]["profile"]
                    for s in range(20)], axis=(0, 1)).round(3).tolist()
        for a in ("k0", "k1", "welfare_universal", "fee*", "tar*")}

    (RUNS / "results_e8.json").write_text(json.dumps(res, indent=1), encoding="utf-8")

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 4))
    x = np.arange(len(arms))
    for j, (space, col) in enumerate((("simple", "#4c72b0"), ("rich", "#dd8452"))):
        m = [res["arms"][f"{space}/{a}"]["cost"] for a in arms]
        ax.bar(x + (j - 0.5) * 0.38, [v[0] for v in m], 0.38, color=col, capsize=2,
               label=f"{'three' if space == 'simple' else 'eight'}-parameter policies",
               yerr=[[v[0] - v[1] for v in m], [v[2] - v[0] for v in m]])
    ax.set_xticks(x, ["private", "universalization", "welfare\n(unilateral)", "welfare\n(joint)",
                      "delay\nsurcharge", "band\ntariff", "planner"])
    ax.set_ylabel("holdout system cost / payment value")
    ax.set_ylim(0.5, None)
    ax.set_title("E8: gates and prices, by policy space (mean, 95% CI, 20 seeds)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(RUNS / "fig_e8.png", dpi=150)
    print(json.dumps({k: res[k] for k in ("R1", "R2", "R3", "R4", "R5")}, indent=1))


if __name__ == "__main__":
    main()
