# Pre-registration — E9: gates against the best available instrument in a shared codebase

Frozen and committed **before** any E9 run. The commit that adds this file is
the timestamp. Every design choice below was made from `runs/cbpilot.jsonl`
only (seeds 1000–1005, `pilot` scenario split) and from equilibrium probes on
the `pilot` split. E9 uses seeds 0–19, the `dev` split for evolution and the
`holdout` split for evaluation. The analysis script
(`src/evortgs/analysis_e9.py`) is committed with this file and was dry-run on
the pilot records only.

## Question

E8 showed that where an operator can price the externality's carrier (delay),
the price beats every gate. Do acceptance gates beat the **best instrument an
operator can levy** when the harm is diffuse, delayed and not attributable to
the agent that caused it?

## Environment (`src/evortgs/codebase.py`)

Six agents (twelve in a secondary regime) each own a module in a shared
codebase and tune three numbers: shortcut intensity `s` (raises own output,
adds coupling), concealed share `m` (coupling invisible to static analysis;
costs the author a share γ of the shortcut's gain and adds 50 % more debt) and
hardening `q` (private protection: costs output, cuts own incident exposure).
All coupling enters one shared debt stock that decays at 15 % per period;
incidents arrive in every module at a rate convex in the debt, and surface in
whichever module they hit. 20 periods per scenario. Holdout families: `base`,
`crunch` (output worth double for a block), `fragile` (incident rate ×1.5),
`spike` (a cascade window, rate ×3), `legacy` (inherited debt). Evolution sees
`base` development scenarios only.

**Why the harm is unattributable.** An incident surfaces in a random module, not
in the module whose coupling caused it, and the stock mixes all agents' past
coupling. The operator observes each agent's visible coupling, each agent's
shipped output, where incidents surface and their loss. It does not observe
policies or concealed coupling.

**Reference.** The optimum is found by exhaustive search over symmetric
policies (11³ grid plus a 9³ refinement) on 64 development scenarios per seed.
On the pilot split, coordinate descent over asymmetric profiles, from the
symmetric optimum and from a specialised start, improved social cost by at most
0.3 %, so the symmetric optimum is treated as the optimum.

## Factors

* **γ (concealment cost)** ∈ {0.25, 1.0}. At γ = 1 concealed shortcuts yield no
  gain, so the proxy charge is in effect a direct price on the externality's
  carrier: a **positive control** that should reproduce E8. At γ = 0.25
  concealment is cheap. **Primary regime: γ = 0.25, n = 6.**
* **n** ∈ {6, 12}. For n = 12 the `activity`, `surface` and `welfare_universal`
  arms are omitted to save compute (pilot: activity is exactly neutral and
  surface is weak).

## Arms (each with the same budget: 40 generations, 4 candidates, 16 simulations)

| Label | Mechanism |
|---|---|
| `k0` | private gate |
| `k1` | universalization (Kantian) gate |
| `welfare` | system cost, unilateral change (central observer) |
| `welfare_universal` | system cost, joint shift (n = 6 only) |
| `proxy` ∈ {0.1, 0.2, 0.4, 0.8} | private gate + charge per unit of the agent's visible coupling |
| `activity` ∈ {0.25, 0.5, 0.75} | private gate + charge per unit of shipped output (n = 6 only) |
| `surface` ∈ {1, 2, 4, 8} | private gate + charge per unit of incident loss surfacing in the agent's own module (n = 6 only) |
| `ambient` ∈ {0.5, 1, 1.5, 2} | private gate + charge per unit of incident loss surfacing in **other** modules, levied on every agent in full |
| `planner` | exhaustive symmetric optimum (reference) |

All charges are transfers: they enter the private cost a gate reads and never
the reported social cost (tested).

**Instrument selection, as in E8.** For each instrument and regime the level is
chosen by mean last-generation **development** cost over seeds, and reported on
holdout (`proxy*` etc.). The **best instrument** is the chosen level with the
lowest development cost across all four instruments; the **best budget-balanced
instrument** is the same over `proxy`, `activity` and `surface`. The **best
own-cost gate** is whichever of `k0`, `k1` has the lower development cost.

## Decision on the ambient tax (recorded in advance)

The ambient tax is the textbook instrument for this information structure
(Segerson 1988; Holmström 1982). At level 1 an agent's private cost differs
from the social cost only by terms its own policy cannot move (tested), so it
induces efficient unilateral incentives and its private-gate runs are
**identical** to the unilateral welfare gate (pilot: identical profiles in every
seed). It breaks the budget: the operator collects about (n − 1) times the
damage. It is **included in the kill criterion**, not excluded on realism
grounds. The comparison against budget-balanced instruments is reported
separately (C5b) and is conditional on an operator being unable to levy an
ambient tax.

## Outcome

Holdout system cost per unit of nominal value, equal-weight mean of five
families, 100 scenarios each. Seeds are the unit (n = 20, paired). 95 %
percentile bootstrap (10 000 resamples), two-sided Wilcoxon signed-rank.
"Clearly" means the interval of the paired difference excludes 0. Equivalence
margin: ±0.002 (about 1 % of the optimum's cost, about 8 % of the
private-to-optimum gap in the pilot).

## Hypotheses and decision rules (per regime unless stated)

* **C1 — there is a dilemma.** `k0` is clearly costlier than `planner`.
  If C1 fails in the primary regime, the environment has no dilemma; say so.
* **C2 — the Kantian gate closes most of it.** `(k0 − k1)/(k0 − planner)` ≥ 0.8
  (ratio of seed means). Pilot: about 0.98 in every regime. In a symmetric
  common-pool game this is expected from Roemer's results; it is a validity
  check, not a finding.
* **C3 — positive control (γ = 1).** `proxy*` is not clearly costlier than the
  best own-cost gate.
* **C4 — the proxy is gamed (γ = 0.25).** `proxy*` is clearly costlier than the
  best own-cost gate, **and** the mean hidden share of coupling across proxy
  levels 0.2, 0.4 and 0.8 exceeds 0.5.
* **C5 — main comparison and kill criterion.** The best own-cost gate is
  clearly cheaper than the best instrument. **Kill criterion: if C5 fails in the
  primary regime, the "acceptance gates as a coordination mechanism against
  pricing" line is closed** and the project pivots or stops, as stated in the
  next-stage notes. Equivalence within ±0.002 is reported alongside.
  **Pilot-based expectation: C5 fails and the kill criterion fires**, because the
  ambient tax matches the Kantian gate (pilot difference +0.0012, interval
  −0.0002 to +0.0026, six seeds).
* **C5b — budget-balanced instruments (conditional result).** The best own-cost
  gate is clearly cheaper than the best budget-balanced instrument. Expected:
  holds at γ = 0.25, fails at γ = 1.
* **C6 — identities (checks, not hypotheses).** `ambient1` and `welfare` give
  identical profiles in every seed; at n = 6 every `activity` level gives the
  same profiles as `k0` (an output charge only rescales the agent's own cost
  when output is worth 1 per unit, as on development scenarios).
* **C7 — does noise favour the gate as n grows?** The interaction
  `(ambient* − gate)_{n=12} − (ambient* − gate)_{n=6}` is clearly positive, for
  each γ. Reasoning: an agent's unilateral effect on others' incident loss is
  diluted across more modules while the joint shift is not. **The pilot did not
  show this; the expectation is that C7 fails.**

## What would count against the pre-registered reading

* C5 holds in the primary regime: gates beat even the ambient tax; the line
  stays open and the reason must be found (noise, multiple equilibria).
* C3 fails: the positive control failed; the environment or the instrument
  tuning is suspect and no conclusion about pricing should be drawn.
* C4 fails: the proxy is not gamed at this concealment cost, and C5b then
  says nothing about hard-to-observe externalities.
* An identity in C6 fails: a bug; stop and investigate before reporting.

## Known limits, stated in advance

* The game is symmetric and, at the optimum, smooth; Kantian optimisation is
  known to be efficient in such common-pool games, so C2 is close to
  guaranteed and says little on its own. Heterogeneous agents, where the
  Kantian rule is not efficient, are not tested here.
* Three bounded parameters per agent; mutation search; agents are risk-neutral
  (the classic objection to ambient taxes, risk aversion under noisy charges,
  is absent by construction).
* The operator is assumed able to commit to an ambient tax and to collect
  (n − 1) times the damage; collusion among agents against it is not modelled.
* The gate needs a sandbox that simulates every agent shifting together;
  whether a real operator could mandate or verify an agent's acceptance rule is
  outside this study.
