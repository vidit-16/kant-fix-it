// Shared-codebase environment: a port of src/evortgs/codebase.py.
//
// Operation order follows the Python line by line, so that given the same
// scenario arrays the two give the same numbers to floating-point precision
// (checked by test/parity.test.mjs against fixtures exported from Python).
//
// Layout: arrays are flat Float64Arrays. A batch holds S scenarios of T
// periods for n agents; cap and u are indexed [s][t][i] -> (s * T + t) * n + i,
// val and mult [s][t] -> s * T + t.

export const INSTRUMENTS = ["proxy", "activity", "surface", "ambient"];
export const FAMILIES = ["base", "crunch", "fragile", "spike", "legacy"];
export const KMAX = 12;

export function config(overrides = {}) {
  return {
    n: 6, T: 20, boost: 0.6,
    conceal_cost: 0.25, conceal_harm: 0.5,
    harden_cost: 0.15, harden_effect: 0.7,
    decay: 0.15, rate: 0.12, convex: 0.3, incident_loss: 0.2,
    heterogeneity: 0.0, exposure_skew: 0.0,
    ...overrides,
  };
}

function rankWeights(n, power) {
  const w = new Float64Array(n);
  let sum = 0;
  for (let i = 0; i < n; i++) { w[i] = (i + 1) ** -power; sum += w[i]; }
  for (let i = 0; i < n; i++) w[i] = (w[i] * n) / sum;
  return w;
}

export const sizes = (cfg) => rankWeights(cfg.n, cfg.heterogeneity);
export const exposure = (cfg) => rankWeights(cfg.n, cfg.exposure_skew);

export function validate(profile, n) {
  if (!Array.isArray(profile) || profile.length !== n) {
    throw new Error("profile size does not match the configuration");
  }
  for (const p of profile) {
    if (p.length !== 3) throw new Error("a profile is n policies of three numbers");
    for (const x of p) {
      if (!Number.isFinite(x) || x < 0 || x > 1) throw new Error("policy parameters must lie in [0, 1]");
    }
  }
}

// Slice scenarios [from, to) of a batch without copying.
export function sliceBatch(b, from, to) {
  const { T, n } = b;
  return {
    S: to - from, T, n,
    cap: b.cap.subarray(from * T * n, to * T * n),
    u: b.u.subarray(from * T * n, to * T * n),
    val: b.val.subarray(from * T, to * T),
    mult: b.mult.subarray(from * T, to * T),
    d0: b.d0.subarray(from, to),
  };
}

export function simulate(b, profile, cfg) {
  const { S, T, n } = b;
  if (n !== cfg.n) throw new Error("batch and configuration disagree on n");
  validate(profile, n);
  const A = sizes(cfg);
  const E = cfg.exposure_skew ? exposure(cfg) : null;
  const s = new Float64Array(n), m = new Float64Array(n);
  const gain = new Float64Array(n), keep = new Float64Array(n);
  const expo = new Float64Array(n), load = new Float64Array(n);
  for (let i = 0; i < n; i++) {
    const [si, mi, qi] = profile[i];
    s[i] = si; m[i] = mi;
    gain[i] = 1.0 + cfg.boost * (2 * si - si * si) * (1.0 - cfg.conceal_cost * mi);
    keep[i] = 1.0 - cfg.harden_cost * qi;
    expo[i] = 1.0 - cfg.harden_effect * qi;
    if (E) expo[i] = expo[i] * E[i];
    load[i] = si * (1.0 + cfg.conceal_harm * mi);
  }

  const cost = new Float64Array(S * n);
  const nominal = new Float64Array(S);
  const charges = new Float64Array(S * n * 4);
  const debt = new Float64Array(S);
  const incidents = new Float64Array(S);
  const visible = new Float64Array(S);
  const hidden = new Float64Array(S);
  const loss = new Float64Array(n);
  const capA = new Float64Array(n);
  const k = new Float64Array(n);

  for (let sc = 0; sc < S; sc++) {
    let D = b.d0[sc];
    let debtSum = 0, inc = 0, vis = 0, hid = 0, nomSum = 0;
    for (let t = 0; t < T; t++) {
      const base = (sc * T + t) * n;
      const v = b.val[sc * T + t];
      const lamBase = cfg.rate * (D + cfg.convex * D * D) * b.mult[sc * T + t];
      let lossSum = 0, nomT = 0, loadSum = 0, kSum = 0, visT = 0, hidT = 0;
      for (let i = 0; i < n; i++) {
        capA[i] = b.cap[base + i] * A[i];
        const lam = lamBase * expo[i];
        // inverse-CDF Poisson, same recurrence as codebase._poisson
        let p = Math.exp(-lam), cdf = p, ki = 0;
        const ui = b.u[base + i];
        for (let j = 1; j <= KMAX; j++) {
          if (ui > cdf) ki += 1;
          p = (p * lam) / j;
          cdf = cdf + p;
        }
        k[i] = ki;
        const down = Math.min(1.0, cfg.incident_loss * ki);
        const planned = capA[i] * keep[i] * gain[i];
        const y = planned * (1.0 - down);
        const nom = v * capA[i] * (1.0 + cfg.boost);
        cost[sc * n + i] += nom - v * y;
        nomT += nom;
        loss[i] = v * planned * down;
        lossSum += loss[i];
        const c = (sc * n + i) * 4;
        charges[c] += capA[i] * s[i] * (1.0 - m[i]);
        charges[c + 1] += y;
        charges[c + 2] += loss[i];
        const coup = capA[i] * s[i];
        visT += coup * (1.0 - m[i]);
        hidT += coup * m[i];
        kSum += ki;
        loadSum += capA[i] * load[i];
      }
      for (let i = 0; i < n; i++) charges[(sc * n + i) * 4 + 3] += lossSum - loss[i];
      nomSum += nomT;
      vis += visT;
      hid += hidT;
      debtSum += D;
      inc += kSum;
      D = (1.0 - cfg.decay) * D + loadSum / n;
    }
    nominal[sc] = nomSum;
    debt[sc] = debtSum / T;
    incidents[sc] = inc / (T * n);
    visible[sc] = vis;
    hidden[sc] = hid;
  }
  return { S, n, cost, nominal, charges, debt, incidents, visible, hidden };
}

// Real cost plus one instrument's charge at one level (a transfer).
export function privateCost(o, instrument, level) {
  if (!instrument || level === 0) return o.cost;
  const j = INSTRUMENTS.indexOf(instrument);
  if (j < 0) throw new Error(`unknown instrument ${instrument}`);
  const out = new Float64Array(o.cost.length);
  for (let x = 0; x < out.length; x++) out[x] = o.cost[x] + level * o.charges[x * 4 + j];
  return out;
}

// Cost function for the evolution loop: real and private cost per scenario and agent.
export function makeCosts(cfg, instrument = null, level = 0) {
  return (b, profile) => {
    const o = simulate(b, profile, cfg);
    return { real: o.cost, priv: privateCost(o, instrument, level), S: b.S, n: b.n };
  };
}
