"""Pre-registered analysis of runs/E12.jsonl (with E10 and E11) -> runs/results_e12.json.

Written before any E12 run; see docs/PREREGISTRATION_E12.md. E12 re-runs the
two Kantian-gate variants E11 got wrong (square root) or left unmatched
(linear with the realized change). Comparators: E10's linear gates, ambient tax
and optimum; E11's log and logit gates. E11's faulty sqrt records enter only the
descriptive comparison of the fault's effect. Differences are ambient - gate.
"""

from __future__ import annotations

import json

import numpy as np

from .analysis import RUNS, boot_mean, paired
from .analysis_e10 import dev, hold, load, spread
from .cb_experiments import E10_SKEWS, E12_SCALES

MARGIN = 0.002
KAPPAS = (0.5, 1.0)
VALID_E11 = ("log", "logit")


def load_scaled(name):
    out = {}
    for line in (RUNS / f"{name}.jsonl").open(encoding="utf-8"):
        r = json.loads(line)
        out.setdefault((r["skew"], f"k{r['kappa']:g}@{r['scale']}"), {})[r["seed"]] = r
    return out


def clearly_positive(ci):
    return ci[1] > 0


def main():
    E10, E11, E12 = load(), load_scaled("E11"), load_scaled("E12")
    res = {"n_runs_e12": sum(len(v) for v in E12.values()), "margin": MARGIN, "skews": {}}
    for skew in E10_SKEWS:
        cells = {f"k{k:g}@linear": E10[(skew, f"k{k:g}")] for k in KAPPAS}
        cells["k0"] = E10[(skew, "k0")]
        for (s, lab), c in E11.items():
            if s == skew and lab.split("@")[1] in VALID_E11:
                cells[lab] = c
        for (s, lab), c in E12.items():
            if s == skew:
                cells[lab] = c
        assert len(cells) == 11, sorted(cells)
        amb, opt = E10[(skew, "ambient1")], E10[(skew, "planner_asym")]
        faulty = {lab: c for (s, lab), c in E11.items() if s == skew and lab.endswith("@sqrt")}
        R = {"arms": {}, "tests": {}, "descriptive": {}}
        for lab, c in sorted(cells.items()):
            R["arms"][lab] = {"cost": boot_mean(hold(c)), "dev_cost": dev(c),
                              "s_by_agent": np.mean([np.asarray(c[s]["profile"]) for s in c],
                                                    axis=0)[:, 0].round(4).tolist()}
        for lab, c in sorted(faulty.items()):
            R["arms"][f"{lab} (E11, faulty)"] = {"cost": boot_mean(hold(c)), "dev_cost": dev(c)}
        R["arms"]["ambient1"] = {"cost": boot_mean(hold(amb)), "dev_cost": dev(amb)}
        R["arms"]["optimum"] = {"cost": boot_mean(hold(opt))}

        best = min(cells, key=lambda lab: dev(cells[lab]))
        R["best_own_cost_gate_all_valid_variants"] = best
        T = R["tests"]
        T["V1_ambient_vs_best_gate"] = paired(hold(amb), hold(cells[best]))
        if skew == 1.5:
            T["V2_log_minus_linear_realized"] = paired(hold(cells["k1@log"]),
                                                       hold(cells["k1@linear_realized"]))
            for sc in ("linear_realized", "sqrt_fixed", "log", "logit"):
                T[f"V3_spread_k1@{sc}_minus_optimum"] = boot_mean(
                    spread(cells[f"k1@{sc}"]) - spread(opt))
        if skew == 0.0:
            for sc in E12_SCALES:
                T[f"V4_k1@{sc}_minus_linear"] = paired(hold(cells[f"k1@{sc}"]),
                                                       hold(cells["k1@linear"]))
        D = R["descriptive"]
        D["convention_effect_k1_linear_realized_minus_linear"] = paired(
            hold(cells["k1@linear_realized"]), hold(cells["k1@linear"]))
        D["fault_effect_k1_sqrt_fixed_minus_e11_sqrt"] = paired(
            hold(cells["k1@sqrt_fixed"]), hold(faulty["k1@sqrt"]))

        d = T["V1_ambient_vs_best_gate"]["diff"]          # ambient - gate
        R["verdicts"] = {
            "V1_ambient_clearly_cheaper": d[2] < 0,
            "gate_clearly_cheaper_beyond_margin": d[1] > 0 and d[0] > MARGIN,
            "within_margin": -MARGIN < d[1] and d[2] < MARGIN,
        }
        if skew == 1.5:
            R["verdicts"]["V2_log_costlier_than_linear_realized"] = clearly_positive(
                T["V2_log_minus_linear_realized"]["diff"])
            R["verdicts"]["V3_distortion_every_valid_scale"] = all(
                clearly_positive(v) for k, v in T.items() if k.startswith("V3_"))
        if skew == 0.0:
            R["verdicts"]["V4_corrected_variants_within_margin_of_linear"] = all(
                -MARGIN < T[k]["diff"][1] and T[k]["diff"][2] < MARGIN
                for k in T if k.startswith("V4_"))
        res["skews"][f"{skew:g}"] = R

    het = [f"{s:g}" for s in E10_SKEWS if s > 0]
    res["strong_line_reopens"] = all(
        res["skews"][k]["verdicts"]["gate_clearly_cheaper_beyond_margin"] for k in het)
    res["closure_robust_to_corrected_variants"] = all(
        res["skews"][k]["verdicts"]["V1_ambient_clearly_cheaper"] for k in het)
    (RUNS / "results_e12.json").write_text(json.dumps(res, indent=1), encoding="utf-8")
    for k, R in res["skews"].items():
        print(k, R["best_own_cost_gate_all_valid_variants"], json.dumps(R["verdicts"]))
    print("strong line reopens:", res["strong_line_reopens"],
          "| closure robust to corrected variants:", res["closure_robust_to_corrected_variants"])


if __name__ == "__main__":
    main()
