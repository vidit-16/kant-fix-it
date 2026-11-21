// Held-out evaluation for the browser engine: a port of src/evortgs/cb_evaluate.py,
// on the browser's own held-out scenarios (same families and distributions).

import { FAMILIES, simulate } from "./model.js";
import { makeBatch } from "./scenarios.js";

const cache = new Map();

function holdout(cfg, family, perFamily) {
  const key = JSON.stringify([cfg, family, perFamily]);
  if (!cache.has(key)) cache.set(key, makeBatch(cfg, family, "holdout", 0, perFamily));
  return cache.get(key);
}

// Mean metrics per family; costs normalised by nominal value. `systemCost` is
// the equal-weight mean over families, the outcome used throughout the report.
export function evaluate(cfg, profile, perFamily = 100) {
  const out = { families: {} };
  let total = 0;
  for (const fam of FAMILIES) {
    const b = holdout(cfg, fam, perFamily);
    const o = simulate(b, profile, cfg);
    let sc = 0, debt = 0, inc = 0, vis = 0, hid = 0;
    for (let x = 0; x < b.S; x++) {
      let c = 0;
      for (let i = 0; i < cfg.n; i++) c += o.cost[x * cfg.n + i];
      sc += c / o.nominal[x];
      debt += o.debt[x]; inc += o.incidents[x]; vis += o.visible[x]; hid += o.hidden[x];
    }
    out.families[fam] = {
      systemCost: sc / b.S, debt: debt / b.S, incidents: inc / b.S,
      hiddenShare: vis + hid > 0 ? hid / (vis + hid) : 0,
    };
    total += sc / b.S;
  }
  out.systemCost = total / FAMILIES.length;
  out.hiddenShare = FAMILIES.reduce((a, f) => a + out.families[f].hiddenShare, 0) / FAMILIES.length;
  return out;
}
