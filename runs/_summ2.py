"""Quick table for rule-level policy runs: python runs/_summ2.py pilot2"""
import json
import sys
from collections import defaultdict

import numpy as np

name = sys.argv[1]
cells = defaultdict(list)
for line in open(f"runs/{name}.jsonl", encoding="utf-8"):
    r = json.loads(line)
    if r["kind"] == "planner":
        lab = "planner"
    elif r["gate"] != "kappa":
        lab = r["gate"]
    else:
        lab = f"k{r['kappa']:g}"
        if r["fee"]:
            lab += f"+fee{r['fee']:g}"
        if r.get("tariff"):
            lab += f"+tar{r['tariff']:g}"
    ev = r["eval"]
    fams = list(ev)
    share = np.mean([ev[f]["settle_share"] for f in fams], axis=0)
    cells[(r.get("rich", False), r["gens"], lab)].append((
        np.mean([ev[f]["system_cost"] for f in fams]),
        np.mean([ev[f]["unsettled"] for f in fams]),
        np.mean([ev[f]["liquidity"] for f in fams]),
        np.mean([ev[f]["delay_ticks"] for f in fams]),
        share[9], share[10:20].sum(),
        r["history"][-1]["dev_system_cost"] if r["history"] else float("nan"),
        np.mean([h["accepted"] for h in r["history"]]) if r["history"] else float("nan"),
    ))
print(f"{'space':6}{'gens':>5} {'arm':20}{'n':>3}{'cost':>8}{'sd':>7}{'unset':>7}{'liq':>7}"
      f"{'delay':>7}{'tick9':>7}{'pm':>7}{'dev':>10}{'acc':>6}")
for (rich, gens, lab), v in sorted(cells.items()):
    a = np.array(v)
    m = a.mean(axis=0)
    print(f"{'rich' if rich else 'simple':6}{gens:>5} {lab:20}{len(v):>3}{m[0]:8.3f}{a[:, 0].std(ddof=1):7.3f}"
          f"{m[1]:7.3f}{m[2]:7.3f}{m[3]:7.2f}{m[4]:7.3f}{m[5]:7.3f}{m[6]:10.0f}{m[7]:6.2f}")
