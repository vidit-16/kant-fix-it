// Phase-1 checks of the browser engine on its own scenarios:
//   1. speed of a full 40-generation run (the in-browser game needs about a second);
//   2. full runs against the published E10 results, 20 seeds per arm;
//   3. how fast concealment appears under a charge on visible coupling.
// Usage: node study.mjs   (writes study-results.json next to this file)

import { writeFileSync } from "node:fs";
import { config, makeCosts } from "./model.js";
import { devSampler } from "./scenarios.js";
import { evoConfig, evolve } from "./evolve.js";
import { evaluate } from "./evaluate.js";

const out = {};

function run(cfg, arm, seed, gens = 40) {
  const e = evoConfig({ generations: gens, gate: arm.gate ?? "kappa", kappa: arm.kappa ?? 0 });
  const r = evolve(devSampler(cfg), makeCosts(cfg, arm.instrument ?? null, arm.level ?? 0), cfg.n, 3, e, seed);
  return r;
}

// 1. speed
{
  const cfg = config();
  const t0 = performance.now();
  const r = run(cfg, { kappa: 1 }, 1);
  const ms = performance.now() - t0;
  out.speed = { full_run_ms: Math.round(ms), sims: r.sims, sims_per_ms: Math.round(r.sims / ms) };
  console.log("speed:", out.speed);
}

// 2. against the published E10 numbers (Python, holdout, 20 seeds)
const published = {
  "0": { k0: 0.2384, k1: 0.2147, ambient1: 0.2156, "proxy0.2": 0.3665 },
  "1.5": { k0: 0.1951, k1: 0.1816, ambient1: 0.1747, "proxy0.2": 0.3383 },
};
const arms = { k0: { kappa: 0 }, k1: { kappa: 1 }, ambient1: { instrument: "ambient", level: 1 },
  "proxy0.2": { instrument: "proxy", level: 0.2 } };
out.compare = {};
for (const skew of ["0", "1.5"]) {
  const cfg = config({ exposure_skew: Number(skew) });
  out.compare[skew] = {};
  for (const [name, arm] of Object.entries(arms)) {
    const costs = [], hidden = [];
    for (let seed = 0; seed < 20; seed++) {
      const ev = evaluate(cfg, run(cfg, arm, seed).profile, 100);
      costs.push(ev.systemCost); hidden.push(ev.hiddenShare);
    }
    const mean = costs.reduce((a, b) => a + b) / costs.length;
    const sd = Math.sqrt(costs.reduce((a, b) => a + (b - mean) ** 2, 0) / (costs.length - 1));
    out.compare[skew][name] = { browser: +mean.toFixed(4), se: +(sd / Math.sqrt(20)).toFixed(4),
      python: published[skew][name], hidden: +(hidden.reduce((a, b) => a + b) / 20).toFixed(3) };
    console.log(`skew ${skew} ${name}:`, out.compare[skew][name]);
  }
}

// 3. concealment over generations under a visible-coupling charge
{
  const cfg = config();
  const gens = 40;
  const byGen = Array.from({ length: gens }, () => []);
  for (let seed = 0; seed < 20; seed++) {
    const r = run(cfg, { instrument: "proxy", level: 0.2 }, seed, gens);
    r.history.forEach((h, g) => byGen[g].push(h.profile.reduce((a, p) => a + p[1], 0) / p_len(h.profile)));
  }
  function p_len(p) { return p.length; }
  out.concealment = byGen.map((v, g) => ({ gen: g, mean_m: +(v.reduce((a, b) => a + b) / v.length).toFixed(3),
    seeds_over_half: v.filter((x) => x > 0.5).length }));
  for (const g of [0, 5, 10, 15, 20, 30, 39]) console.log("gen", g, out.concealment[g]);
}

writeFileSync(new URL("./study-results.json", import.meta.url), JSON.stringify(out, null, 1));
