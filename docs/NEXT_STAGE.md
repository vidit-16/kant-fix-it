# Next stage — working notes

Read [PROJECT.md](PROJECT.md) first; it is the canonical record. This file only
says what to do next and what not to repeat. Fold its content into PROJECT.md
(§7 and the decision log) once the stage is under way, then delete it.

## Where things stand

* Two pre-registered studies in the payment environment (E1–E6, E8) plus one
  exploratory ablation (E7). 1,570 runs, 40 tests, all committed.
* Settled: the acceptance gate changes collective outcomes a lot; a
  universalization gate recovers about half the loss while reading only own
  cost; evaluating joint moves matters more than seeing others' costs.
* Settled against the original idea: where an operator can charge for delay,
  that charge beats every gate, with three-parameter and eight-parameter
  policies. Reason: a charge on settlement time is a charge on the externality
  itself.
* Therefore gates can only matter where nobody can price the externality.
  The payment environment cannot show that. Do not run more gate-versus-price
  experiments in it.

## Recommended stage: a second environment without a usable price

Goal: test whether gates beat the *best available* instrument when harm is
diffuse, delayed and not attributable to the agent that caused it.

Requirements for the environment (reject a design that misses any):

1. **The price is not excluded by decree.** Include the strongest instrument an
   operator could realistically levy given what it can observe (for example a
   charge on a noisy or aggregate signal) and tune it on development data, as
   the surcharge was. If that instrument matches the gates, report it and stop.
2. **Harm is unattributable by construction, with a reason.** For example each
   agent's change raises a shared failure rate or shared maintenance load that
   is only observed in aggregate and with delay.
3. **Known optimum or strong reference.** Small enough that a planner or
   exhaustive search gives a trustworthy reference; the weak planner was a
   problem in E1 and E8.
4. **Closer to self-improving agents than payments.** Candidates: agents
   sharing a codebase (speed-ups that add coupling), a shared context or
   compute budget, a shared evaluation harness that agents can overfit.
5. **Cheap.** Thousands of simulations per run, pure Python, deterministic.

Order of work:

1. Prior-art check for the chosen environment (commons games with unobservable
   contributions, moral hazard in teams, Holmström 1982; GovSim; FRAIL). State
   plainly what is already known.
2. Build the environment with invariant tests, reusing `evolve.py` gates and
   the dev/holdout/pilot split unchanged where possible.
3. Sanity gate before anything else: confirm private gates are inefficient
   against the reference. If not, the environment has no dilemma; say so.
4. Pilot on pilot seeds only; choose budget and instrument grids.
5. Freeze a pre-registration and commit it before any confirmatory run.
6. Run, analyse with a script written before results exist, update PROJECT.md
   and REPORT.md, commit.

Kill criterion to register in advance: if the best realistic instrument is
within noise of the best own-cost gate, the "gates as coordination mechanism"
line is closed and the project should pivot or stop.

## Lower-priority items (only if asked)

* Better optimiser for eight-parameter policies (all arms degrade at fixed
  budget; cross-space comparisons are search-limited).
* Noise-aware gates as a registered factor (E7 follow-up).
* Language-model proposers. Needs the owner's API key, model choice and
  spending cap; do not start without all three. Do it in the second
  environment, not in payments.
* Heterogeneous banks under a uniform price.

## Working rules that produced trustworthy results so far

* Pilot seeds 1000–1005 and the `pilot` split for every design choice;
  confirmatory seeds 0–19; holdout never visible to evolution (tested).
* Pre-register hypotheses, decision rules and a "what would count against
  this" section; commit before running; report failed predictions as failed.
* Same simulation budget for every arm, asserted in tests.
* Instrument levels chosen on development cost, reported on holdout.
* Label anything decided after seeing data as post hoc.
* Check that old records still reproduce after any engine change.
* Commit `src/` before launching runs so records are not flagged dirty.
* No novelty, "first" or breakthrough claims; nothing here is evidence about
  recursive self-improvement.

## Standing constraints from the project owner

* No reference to any AI tool or vendor in commits, trailers, code comments,
  documents or metadata. Commits use the configured Git identity.
* No live financial APIs, credentials or real money. Agents never modify the
  evaluator, accounting, manifests or budget. No execution of generated code
  without a sandbox design agreed first.
* One canonical document: PROJECT.md.
* Work autonomously; ask only for consequential decisions or external
  authorisation (keys, spending, publication).

## Practical

* Windows, Git Bash and PowerShell; `uv run pytest`, `uv run python -m
  evortgs.experiments <name>`; long runs go in the background (E8 took 40
  minutes on this machine).
* Multi-line Python inside shell heredocs breaks on apostrophes; write a
  script file instead.
