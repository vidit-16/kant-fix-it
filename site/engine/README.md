# Browser engine

The shared-codebase model and the gated evolution loop, ported from
`src/evortgs` to plain JavaScript (no dependencies) so the website can run real
experiments in the browser.

* `model.js`: the codebase simulation and instruments (`codebase.py`).
* `scenarios.js`: seeded scenario families. Same distributions as Python, but
  the browser's own random stream.
* `evolve.js`: the gated evolution loop, every gate and the E11 scales (`gates.py`).
* `evaluate.js`: held-out scoring (`cb_evaluate.py`).

## Is it the same model?

`npm test` checks the port against fixtures exported from the research code
(`uv run python site/engine/fixtures/export.py` from the repository root):

* `simulate` matches Python on 75 cases (5 configurations by 5 scenario
  families), to floating-point precision;
* sums follow NumPy's pairwise order exactly;
* given Python's random draws, the loop makes the same accept and reject
  decisions as Python in 10 runs covering every gate, the rescaled Kantian
  gates, three instruments and unequal exposure.

`node study.mjs` runs the engine on its own scenarios and compares it with
the published E10 results (`study-results.json`): every arm lands within
sampling noise of the paper, with the same ordering. A full 40-generation run
takes about half a second on a laptop.
