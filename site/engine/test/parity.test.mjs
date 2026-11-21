// The browser engine against the research code. Fixtures come from
// fixtures/export.py, which calls src/evortgs directly.
import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { config, makeCosts, simulate } from "../model.js";
import { evoConfig, evolve, npSum } from "../evolve.js";

const fx = JSON.parse(readFileSync(new URL("../fixtures/parity.json", import.meta.url), "utf8"));

const toBatch = (b) => ({ S: b.S, T: b.T, n: b.n, cap: Float64Array.from(b.cap), u: Float64Array.from(b.u),
  val: Float64Array.from(b.val), mult: Float64Array.from(b.mult), d0: Float64Array.from(b.d0) });

function close(actual, expected, what, rel = 1e-12) {
  assert.equal(actual.length, expected.length, `${what}: length`);
  for (let i = 0; i < expected.length; i++) {
    const tol = rel * Math.max(1, Math.abs(expected[i]));
    assert.ok(Math.abs(actual[i] - expected[i]) <= tol, `${what}[${i}]: ${actual[i]} vs ${expected[i]}`);
  }
}

test("simulate matches the Python model on 75 cases", () => {
  for (const c of fx.simulate) {
    const o = simulate(toBatch(c.batch), c.profile, config(c.cfg));
    const tag = `${c.family} n=${c.cfg.n} skew=${c.cfg.exposure_skew}`;
    for (const k of ["cost", "nominal", "charges", "debt", "incidents", "visible", "hidden"]) close(o[k], c[k], `${tag} ${k}`);
  }
});

test("sums follow NumPy's reduction exactly", () => {
  for (const c of fx.sums) {
    assert.equal(npSum(c.a), c.sum, `n=${c.a.length}`);
    assert.equal(npSum(c.a) / c.a.length, c.mean, `mean n=${c.a.length}`);
  }
});

test("the evolution loop makes Python's decisions, given Python's draws", () => {
  for (const c of fx.loops) {
    const cfg = config(c.cfg);
    const batches = c.batches.map(toBatch);
    const r = evolve(null, makeCosts(cfg, c.instrument, c.level), cfg.n, 3, evoConfig(c.evo), c.seed,
      { streams: { init: c.init, deltas: c.deltas.map((d) => Float64Array.from(d)), batches } });
    assert.equal(r.sims, c.sims, `${c.case}: budget`);
    c.history.forEach((h, g) => {
      assert.equal(r.history[g].accepted, h.accepted, `${c.case} gen ${g}: accepted`);
      close([r.history[g].dev_system_cost], [h.dev_system_cost], `${c.case} gen ${g}: cost`);
      close(r.history[g].profile.flat(), h.profile.flat(), `${c.case} gen ${g}: profile`);
    });
    close(r.profile.flat(), c.final.flat(), `${c.case}: final profile`);
  }
});
