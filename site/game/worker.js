// Runs the real engine off the main thread and streams each generation back.
import { config, makeCosts } from "../engine/model.js";
import { devSampler, rng } from "../engine/scenarios.js";
import { evoConfig, evolve } from "../engine/evolve.js";
import { evaluate } from "../engine/evaluate.js";

export const RULES = {
  none: { gate: "kappa", kappa: 0 },
  conscience: { gate: "kappa", kappa: 1 },
  visible: { gate: "kappa", kappa: 0, instrument: "proxy" },
  damage: { gate: "kappa", kappa: 0, instrument: "ambient" },
};

self.onmessage = ({ data }) => {
  const { rule, level, skew, seed, honest } = data;
  const r = RULES[rule];
  const cfg = config({ exposure_skew: skew });
  const r0 = rng([seed, 99]);
  const init = Array.from({ length: cfg.n }, () =>
    honest ? [0.3 + 0.4 * r0.random(), 0, 0.3 * r0.random()] : [r0.random(), r0.random(), r0.random()]);
  const res = evolve(devSampler(cfg), makeCosts(cfg, r.instrument ?? null, r.instrument ? level : 0),
    cfg.n, 3, evoConfig({ gate: r.gate, kappa: r.kappa }), seed, {
      init,
      onGeneration: (rec) => self.postMessage({ type: "gen", gen: rec.gen, profile: rec.profile, accepted: rec.accepted }),
    });
  self.postMessage({ type: "gen", gen: res.history.length, profile: res.profile, accepted: 0 });
  const ev = evaluate(cfg, res.profile, 60);
  self.postMessage({ type: "done", profile: res.profile, systemCost: ev.systemCost, hiddenShare: ev.hiddenShare });
};
