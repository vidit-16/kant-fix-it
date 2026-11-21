// Gated evolution loop: a port of src/evortgs/gates.py (evolve_env).
//
// Each generation every agent proposes K Gaussian mutations of its policy,
// scores each on 2*M development scenarios with its gate, and keeps the best
// one if its score is negative. All agents update together.
//
// `streams` replaces the random draws (initial profile, mutations, scenario
// batches) with given ones, so the parity test can feed Python's exact draws
// and demand identical decisions.

import { sliceBatch } from "./model.js";
import { rng as makeRng } from "./scenarios.js";

export const SCALES = {
  linear: null,
  log: [(x) => Math.log(x + 0.05), (y) => Math.exp(y) - 0.05],
  sqrt: [Math.sqrt, (y) => y * y],
  logit: [(x) => Math.log((x + 0.05) / (1.05 - x)),
    (y) => (1.05 * Math.exp(y) - 0.05) / (1 + Math.exp(y))],
};

export function evoConfig(overrides = {}) {
  return { generations: 40, K: 4, M: 8, sigma: 0.15, sigma_end: 0.03,
    gate: "kappa", kappa: 0.0, scale: "linear", ...overrides };
}

const clip = (x) => (x < 0 ? 0 : x > 1 ? 1 : x);

function universal(cur, i, cand, d, n, dim, scale) {
  if (scale === "linear") {
    return cur.map((p) => p.map((x, a) => clip(x + d[a])));
  }
  const [g, ginv] = SCALES[scale];
  const step = cand.map((c, a) => g(c) - g(cur[i][a]));
  return cur.map((p, j) => (j === i ? cand : p.map((x, a) => clip(ginv(g(x) + step[a])))));
}

// NumPy's float reduction (pairwise_sum): left to right below eight
// elements; from eight up, eight running lanes combined as a tree, then the
// remainder; halves recursively above 128 elements.
// Matching it makes means of differences come out bit for bit as in Python;
// test/parity.test.mjs checks it against NumPy on arrays of many lengths.
function pairwise(a, lo, n) {
  if (n < 8) { let s = -0; for (let i = 0; i < n; i++) s += a[lo + i]; return s; }
  if (n > 128) {
    let h = n >> 1; h -= h % 8;
    return pairwise(a, lo, h) + pairwise(a, lo + h, n - h);
  }
  const r = [];
  for (let j = 0; j < 8; j++) r.push(a[lo + j]);
  let i = 8;
  for (; i < n - (n % 8); i += 8) for (let j = 0; j < 8; j++) r[j] += a[lo + i + j];
  let s = ((r[0] + r[1]) + (r[2] + r[3])) + ((r[4] + r[5]) + (r[6] + r[7]));
  for (; i < n; i++) s += a[lo + i];
  return s;
}
export function npSum(a) {
  return a.length === 0 ? 0 : pairwise(a, 0, a.length);
}
const npMean = (a) => npSum(a) / a.length;

// Mean over scenarios of agent i's private cost difference; c covers base
// scenarios [offset, offset + c.S).
function meanDiff(c, base, i, offset = 0) {
  const d = new Float64Array(c.S);
  for (let sc = 0; sc < c.S; sc++) d[sc] = c.priv[sc * c.n + i] - base.priv[(sc + offset) * c.n + i];
  return npMean(d);
}

function rowSums(x, S, n) {
  const out = new Float64Array(S);
  for (let sc = 0; sc < S; sc++) { let s = 0; for (let j = 0; j < n; j++) s += x[sc * n + j]; out[sc] = s; }
  return out;
}

function totalRealDiffMean(c, base) {
  const a = rowSums(c.real, c.S, c.n), b = rowSums(base.real, c.S, c.n);
  const d = new Float64Array(c.S);
  for (let sc = 0; sc < c.S; sc++) d[sc] = a[sc] - b[sc];
  return npMean(d);
}

export function evolve(batch, costs, n, dim, cfg, seed, { init = null, streams = null, onGeneration = null } = {}) {
  if (!(cfg.scale in SCALES)) throw new Error(`unknown scale ${cfg.scale}`);
  const r = makeRng([seed, 7919]);
  let profile = streams ? streams.init.map((p) => [...p])
    : init ? init.map((p) => [...p])
    : Array.from({ length: n }, () => Array.from({ length: dim }, () => r.random()));
  const S = 2 * cfg.M;
  const history = [];
  let sims = 0;

  for (let g = 0; g < cfg.generations; g++) {
    const scns = streams ? streams.batches[g] : batch(seed * 100000 + g * S, S);
    const frac = g / Math.max(1, cfg.generations - 1);
    const sig = cfg.sigma + (cfg.sigma_end - cfg.sigma) * frac;
    let deltas;
    if (streams) deltas = streams.deltas[g];
    else {
      deltas = new Float64Array(n * cfg.K * dim);
      for (let x = 0; x < deltas.length; x++) deltas[x] = sig * r.normal();
    }
    const base = costs(scns, profile);
    sims += S;
    const genCost = npMean(rowSums(base.real, S, n));
    const next = profile.map((p) => [...p]);
    let accepted = 0;
    for (let i = 0; i < n; i++) {
      let bestScore = 0, bestPol = null;
      for (let k = 0; k < cfg.K; k++) {
        const d = Array.from({ length: dim }, (_, a) => deltas[(i * cfg.K + k) * dim + a]);
        const cand = profile[i].map((x, a) => clip(x + d[a]));
        const uni = profile.map((p, j) => (j === i ? cand : p));
        const needAll = cfg.gate === "welfare_universal" || (cfg.gate === "kappa" && cfg.kappa > 0);
        const allp = needAll ? universal(profile, i, cand, d, n, dim, cfg.gate === "kappa" ? cfg.scale : "linear") : null;
        let score;
        if (cfg.gate === "kappa") {
          if (cfg.kappa <= 0) score = meanDiff(costs(scns, uni), base, i);
          else if (cfg.kappa >= 1) score = meanDiff(costs(scns, allp), base, i);
          else {
            const h = cfg.M;
            const cu = costs(sliceBatch(scns, 0, h), uni);
            const ck = costs(sliceBatch(scns, h, S), allp);
            score = (1 - cfg.kappa) * meanDiff(cu, base, i, 0)
              + cfg.kappa * meanDiff(ck, base, i, h);
          }
        } else if (cfg.gate === "welfare") {
          score = totalRealDiffMean(costs(scns, uni), base);
        } else if (cfg.gate === "welfare_universal") {
          score = totalRealDiffMean(costs(scns, allp), base);
        } else {
          throw new Error(`unknown gate ${cfg.gate}`);
        }
        sims += S;
        if (score < bestScore) { bestScore = score; bestPol = cand; }
      }
      if (bestPol !== null) { next[i] = bestPol; accepted += 1; }
    }
    const rec = { gen: g, dev_system_cost: genCost, accepted, profile: profile.map((p) => [...p]) };
    history.push(rec);
    if (onGeneration) onGeneration(rec, next);
    profile = next;
  }
  return { profile, history, sims };
}
