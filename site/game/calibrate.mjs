// Calibrates level goals: runs the game's exact setup (8-generation chunks,
// sigma 0.09, the board's 12 'site' scenarios and reference points) for each
// rule, and reports the score trajectory and whether each goal is met.
// Usage: node site/game/calibrate.mjs
import { config, simulate, makeCosts } from "../engine/model.js";
import { makeBatch, devSampler, rng } from "../engine/scenarios.js";
import { evoConfig, evolve } from "../engine/evolve.js";

const RULES = { none: [0, null], conscience: [1, null], visible: [0, "proxy"], damage: [0, "ambient"] };

function refs(skew) {
  const cfg = config({ exposure_skew: skew });
  const b = makeBatch(cfg, "base", "site", 0, 12);
  const cost = (P) => {
    const o = simulate(b, P, cfg);
    let c = 0, v = 0, h = 0;
    for (let s = 0; s < b.S; s++) { let x = 0; for (let i = 0; i < 6; i++) x += o.cost[s * 6 + i]; c += x / o.nominal[s]; v += o.visible[s]; h += o.hidden[s]; }
    return { cost: c / b.S, hidden: v + h > 0 ? h / (v + h) : 0 };
  };
  const nothing = cost(Array(6).fill([0.97, 0, 0.97])).cost;
  let best = Infinity, bp = null;
  for (let si = 0; si <= 20; si++) for (const q of [0, 0.25, 0.5]) {
    const c = cost(Array(6).fill([si / 20, 0, q])).cost;
    if (c < best) { best = c; bp = Array(6).fill([si / 20, 0, q]); }
  }
  let P = bp;
  if (skew > 0) for (let sw = 0; sw < 2; sw++) for (let i = 0; i < 6; i++)
    for (let si = 0; si <= 20; si++) for (const q of [0, 0.25, 0.5, 0.75]) {
      const Q = P.map((p, j) => (j === i ? [si / 20, 0, q] : p));
      const c = cost(Q).cost;
      if (c < best) { best = c; P = Q; }
    }
  return { cfg, cost, nothing, best };
}

function play(skew, rule, level, seed, gens, init) {
  const R = refs(skew), [kappa, inst] = RULES[rule];
  let P = init ?? (() => { const r0 = rng([seed, 99]); return Array.from({ length: 6 }, () => [0.3 + 0.4 * r0.random(), 0, 0.3 * r0.random()]); })();
  const out = [];
  for (let chunk = 0; out.length < gens; chunk++) {
    evolve(devSampler(R.cfg), makeCosts(R.cfg, inst, inst ? level : 0), 6, 3,
      evoConfig({ generations: 8, kappa, sigma: 0.09, sigma_end: 0.09 }), seed + chunk * 101, {
        init: P, onGeneration: (_r, next) => {
          P = next;
          const m = R.cost(next);
          out.push({ score: (REF[skew].nothing - m.cost) / (REF[skew].nothing - REF[skew].best) * 100, hidden: m.hidden, cost: m.cost });
        },
      });
  }
  return out.slice(0, gens);
}

function firstHold(series, ok, hold) {
  let run = 0;
  for (let g = 0; g < series.length; g++) { run = ok(series[g]) ? run + 1 : 0; if (run >= hold) return g + 1; }
  return null;
}

const LEVELS = [
  { name: "1 stop them", skew: 0, gens: 60, hold: 8, ok: (x) => x.score >= 80, rules: [["none"], ["conscience"], ["damage", 1], ["visible", 0.4]] },
  { name: "2 hiding", skew: 0, gens: 60, hold: 6, init: Array(6).fill([0.92, 0.9, 0.6]), ok: (x) => x.score >= 70 && x.hidden < 0.15, rules: [["visible", 0.4], ["none"], ["conscience"], ["damage", 1]] },
  { name: "3 one module", skew: 1.5, gens: 60, hold: 8, ok: (x) => x.score >= 85, rules: [["none"], ["conscience"], ["damage", 1]] },
  { name: "4 price is wrong", skew: 0.75, gens: 60, hold: 8, ok: (x) => x.score >= 85, rules: [["damage", 2], ["damage", 1.4], ["damage", 1], ["damage", 0.7], ["damage", 0.4]] },
];

const REF = process.argv.includes('--refs') ? null : JSON.parse(await import('node:fs').then((fs) => fs.readFileSync(new URL('./board-refs.json', import.meta.url), 'utf8')));
if (REF) for (const L of LEVELS.filter((l) => !process.argv[2] || l.name.startsWith(process.argv[2]))) {
  console.log(`\n== level ${L.name}`);
  for (const [rule, level] of L.rules) {
    const met = [], tails = [];
    for (let seed = 1; seed <= 8; seed++) {
      const s = play(L.skew, rule, level ?? 0, seed * 7919, L.gens, L.init);
      met.push(firstHold(s, L.ok, L.hold));
      const last = s.slice(-15);
      tails.push(Math.round(last.reduce((a, x) => a + x.score, 0) / last.length));
    }
    const wins = met.filter((x) => x !== null);
    console.log(`${(rule + (level ? " " + level : "")).padEnd(14)} goal met ${wins.length}/8` +
      (wins.length ? ` (by gen ${Math.min(...wins)}-${Math.max(...wins)})` : "") + ` | late score ${tails.join(" ")}`);
  }
}

// ---- reference points for the board ------------------------------------------
// "doing nothing": the mean late cost of selfish agents (rule none), 8 seeds;
// "best possible": the lowest cost found by any of (a) a symmetric grid,
// (b) the late profiles every rule reached, then polished by per-agent
// coordinate descent on a fine grid. Printed as constants for game.js.
export function boardRefs(skew) {
  const R = refs(skew);
  const lateCost = (s) => s.slice(-15).reduce((a, x) => a + x.cost, 0) / 15;
  const runs = (rule, level) => Array.from({ length: 8 }, (_, k) => k + 1).map((seed) => {
    const [kappa, inst] = RULES[rule];
    let P = (() => { const r0 = rng([seed * 7919, 99]); return Array.from({ length: 6 }, () => [0.3 + 0.4 * r0.random(), 0, 0.3 * r0.random()]); })();
    const costs = [];
    for (let chunk = 0; costs.length < 60; chunk++) {
      evolve(devSampler(R.cfg), makeCosts(R.cfg, inst, inst ? level : 0), 6, 3,
        evoConfig({ generations: 8, kappa, sigma: 0.09, sigma_end: 0.09 }), seed * 7919 + chunk * 101,
        { init: P, onGeneration: (_r, next) => { P = next; costs.push({ cost: R.cost(next).cost }); } });
    }
    return { costs, final: P };
  });
  const selfish = runs("none", 0);
  const nothing = selfish.reduce((a, r) => a + lateCost(r.costs), 0) / selfish.length;
  const pool = [...selfish, ...runs("conscience", 0), ...runs("damage", 1)].map((r) => r.final);
  let bestP = pool.reduce((a, P) => (R.cost(P).cost < R.cost(a).cost ? P : a));
  let best = Math.min(R.cost(bestP).cost, R.best);
  for (let sw = 0; sw < 3; sw++) for (let i = 0; i < 6; i++)
    for (let si = 0; si <= 40; si++) for (const q of [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]) {
      const Q = bestP.map((p, j) => (j === i ? [si / 40, 0, q] : p));
      const c = R.cost(Q).cost;
      if (c < best) { best = c; bestP = Q; }
    }
  return { nothing: +nothing.toFixed(5), best: +best.toFixed(5) };
}

if (process.argv.includes("--refs")) {
  const out = {};
  for (const skew of [0, 0.75, 1.5]) out[skew] = boardRefs(skew);
  console.log(JSON.stringify(out));
}
