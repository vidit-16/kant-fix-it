# EvoRTGS

A small, deterministic testbed for one question: when several agents in a
shared environment each improve their own policy through a
propose–evaluate–accept loop, how much does the **acceptance gate** decide the
collective outcome?

The environment is a stylized real-time gross settlement (RTGS) payment
network. It is a simulator only: no real payment system, data or money is
involved, and results say nothing about any real system.

* [docs/PROJECT.md](docs/PROJECT.md) — canonical project document: decisions,
  prior-art audit, results, open questions.
* [docs/PREREGISTRATION.md](docs/PREREGISTRATION.md),
  [docs/PREREGISTRATION_E8.md](docs/PREREGISTRATION_E8.md) — protocols frozen
  before the confirmatory runs.
* [docs/REPORT.md](docs/REPORT.md) — paper-style report.
* `runs/` — one JSON line per run, `results.json`, figures.

## Headline result

With proposals, search budget and environment fixed, the gate alone moves
holdout system cost by 23 %. A gate that reads only the agent's own cost under
the counterfactual "everyone makes this same change" recovers about half of the
loss caused by private gates, and the gain transfers to five unseen shock
families. A conventional delay surcharge with private gates beats every gate
tested, with three-parameter and with eight-parameter rule-level policies; a
coarser two-band tariff does not hold up with the richer policies. Details and
caveats are in the project document.

## Run

```bash
uv sync
uv run pytest
uv run python -m evortgs.experiments E1 E2 E3 E4 E5 E6 E7 E8
uv run python -m evortgs.analysis
uv run python -m evortgs.analysis_e8
```

## Layout

```
src/evortgs/sim.py          settlement engine, costs, invariants
src/evortgs/scenarios.py    scenario families, development/holdout split
src/evortgs/evolve.py       gated evolution loop
src/evortgs/evaluate.py     locked holdout evaluation
src/evortgs/experiments.py  experiment definitions and runner
src/evortgs/analysis.py     statistics and figures (E1-E6)
src/evortgs/analysis_e8.py  statistics and figure (E8)
tests/                      accounting, determinism, protocol isolation
```
