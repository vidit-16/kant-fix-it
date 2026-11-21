// Runs the real engine off the main thread, in chunks, so the page can keep the
// simulation going indefinitely and switch rules mid-run from the current state.
import { config, makeCosts } from "../engine/model.js";
import { devSampler, rng } from "../engine/scenarios.js";
import { evoConfig, evolve } from "../engine/evolve.js";

const RULES = {
  none: { kappa: 0 },
  conscience: { kappa: 1 },
  visible: { kappa: 0, instrument: "proxy" },
  damage: { kappa: 0, instrument: "ambient" },
};

self.onmessage = ({ data }) => {
  const { job, rule, level, skew, seed, init, honest, gens, genOffset } = data;
  const r = RULES[rule];
  const cfg = config({ exposure_skew: skew });
  let start = init;
  if (!start) {
    const r0 = rng([seed, 99]);
    start = Array.from({ length: cfg.n }, () =>
      honest ? [0.3 + 0.4 * r0.random(), 0, 0.3 * r0.random()] : [r0.random(), r0.random(), r0.random()]);
  }
  // A chunk is a short run continuing from `start`; mutation size stays at the
  // mid-run level so agents keep adapting however long the page runs.
  evolve(devSampler(cfg), makeCosts(cfg, r.instrument ?? null, r.instrument ? level : 0),
    cfg.n, 3, evoConfig({ generations: gens, kappa: r.kappa, sigma: 0.09, sigma_end: 0.09 }),
    seed + genOffset, {
      init: start,
      onGeneration: (_rec, next) => self.postMessage({ job, profile: next }),
    });
  self.postMessage({ job, chunkDone: true });
};
