// Scenario generation for the browser engine.
//
// The distributions and families are those of src/evortgs/codebase.py, but the
// random stream is our own (NumPy's generator cannot be reproduced here), so a
// browser scenario with index i is not the Python scenario with index i. Exact
// parity is tested on scenario arrays exported from Python; the browser's own
// scenarios are checked statistically against the published results.

import { FAMILIES } from "./model.js";

const SPLIT_ID = { dev: 11, holdout: 23, pilot: 37, site: 53 };

// xoshiro128** seeded through splitmix32 from a list of integers.
export function rng(keys) {
  let h = 0x9e3779b9 | 0;
  const mix = (x) => {
    h = (h + (x | 0) + 0x9e3779b9) | 0;
    let z = h;
    z = Math.imul(z ^ (z >>> 16), 0x85ebca6b);
    z = Math.imul(z ^ (z >>> 13), 0xc2b2ae35);
    return (z ^ (z >>> 16)) >>> 0;
  };
  for (const k of keys) mix(Math.floor(k) & 0xffffffff), mix(Math.floor(k / 2 ** 32));
  let a = mix(1), b = mix(2), c = mix(3), d = mix(4);
  if ((a | b | c | d) === 0) a = 1;
  const next = () => {
    const r = Math.imul(Math.imul(b, 5) << 7 | Math.imul(b, 5) >>> 25, 9) >>> 0;
    const t = b << 9;
    c ^= a; d ^= b; b ^= c; a ^= d; c ^= t;
    d = d << 11 | d >>> 21;
    return r;
  };
  // 53 random bits -> uniform on [0, 1)
  const random = () => ((next() >>> 5) * 67108864 + (next() >>> 6)) / 9007199254740992;
  let spare = null;
  const normal = () => {
    if (spare !== null) { const z = spare; spare = null; return z; }
    let u = 0;
    while (u === 0) u = random();
    const r = Math.sqrt(-2 * Math.log(u)), th = 2 * Math.PI * random();
    spare = r * Math.sin(th);
    return r * Math.cos(th);
  };
  const integer = (lo, hi) => lo + Math.floor(random() * (hi - lo)); // [lo, hi)
  return { random, normal, integer };
}

// One scenario written into a batch at position sc.
function fill(b, sc, cfg, family, split, index) {
  const { T, n } = cfg;
  const r = rng([SPLIT_ID[split], FAMILIES.indexOf(family), index, n, T,
    Math.round(cfg.heterogeneity * 1000), 4242]);
  for (let x = 0; x < T * n; x++) b.cap[sc * T * n + x] = Math.exp(-0.02 + 0.2 * r.normal());
  for (let t = 0; t < T; t++) { b.val[sc * T + t] = 1; b.mult[sc * T + t] = 1; }
  b.d0[sc] = 0;
  if (family === "crunch") {
    const a = r.integer(0, T - Math.floor(T / 4));
    for (let t = a; t < Math.min(T, a + Math.floor(T / 4)); t++) b.val[sc * T + t] = 2;
  } else if (family === "fragile") {
    for (let t = 0; t < T; t++) b.mult[sc * T + t] = 1.5;
  } else if (family === "spike") {
    const a = r.integer(Math.floor(T / 4), T - Math.floor(T / 5));
    for (let t = a; t < Math.min(T, a + Math.floor(T / 5)); t++) b.mult[sc * T + t] = 3;
  } else if (family === "legacy") {
    b.d0[sc] = 2 + 3 * r.random();
  } else if (family !== "base") {
    throw new Error(`unknown family ${family}`);
  }
  for (let x = 0; x < T * n; x++) b.u[sc * T * n + x] = r.random();
}

export function makeBatch(cfg, family, split, start, count) {
  if (!(split in SPLIT_ID)) throw new Error(`unknown split ${split}`);
  const { T, n } = cfg;
  const b = {
    S: count, T, n,
    cap: new Float64Array(count * T * n), u: new Float64Array(count * T * n),
    val: new Float64Array(count * T), mult: new Float64Array(count * T),
    d0: new Float64Array(count),
  };
  for (let i = 0; i < count; i++) fill(b, i, cfg, family, split, start + i);
  return b;
}

// The only scenario source the evolution loop gets: base family, never holdout.
export function devSampler(cfg, split = "dev") {
  if (split === "holdout") throw new Error("the evolution loop may not sample holdout scenarios");
  return (start, count) => makeBatch(cfg, "base", split, start, count);
}
