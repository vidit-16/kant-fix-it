// "Try to stop them": phase-2 prototype. Rough visuals on purpose.
import { config, simulate, exposure } from "../engine/model.js";
import { makeBatch } from "../engine/scenarios.js";

// Published holdout results (E10, Python, 20 seeds): doing nothing and the optimum.
const REFERENCE = {
  0: { nothing: 0.2384, best: 0.2137 },
  0.75: { nothing: 0.2340, best: 0.2015 },
  1.5: { nothing: 0.1951, best: 0.1749 },
};
const LEVELS = { visible: [0.05, 0.8, 0.4], damage: [0.25, 2, 1] }; // min, max, default

const $ = (s) => document.querySelector(s);
const ui = {
  rule: $("#rule"), level: $("#level"), levelOut: $("#levelOut"), levelRow: $("#levelRow"),
  skew: $("#skew"), honest: $("#honest"), run: $("#run"), xray: $("#xray"), speed: $("#speed"),
  board: $("#board"), cost: $("#cost"), hid: $("#hid"), gen: $("#gen"), score: $("#score"),
};

let state = null;
const visBatches = {};

function visBatch(skew) {
  const cfg = config({ exposure_skew: skew });
  if (!visBatches[skew]) visBatches[skew] = makeBatch(cfg, "base", "site", 0, 12);
  return { cfg, b: visBatches[skew] };
}

// What the board shows for one profile: incident loss per module, system cost, hidden share.
function metrics(profile, skew) {
  const { cfg, b } = visBatch(skew);
  const o = simulate(b, profile, cfg);
  const n = cfg.n, perAgent = new Array(n).fill(0);
  let cost = 0, vis = 0, hid = 0;
  for (let s = 0; s < b.S; s++) {
    let c = 0;
    for (let i = 0; i < n; i++) {
      c += o.cost[s * n + i];
      perAgent[i] += o.charges[(s * n + i) * 4 + 2] / o.nominal[s] * n / b.S;
    }
    cost += c / o.nominal[s] / b.S;
    vis += o.visible[s]; hid += o.hidden[s];
  }
  return { perAgent, cost, hidden: vis + hid > 0 ? hid / (vis + hid) : 0 };
}

function syncLevel() {
  const r = ui.rule.value;
  ui.levelRow.hidden = !(r in LEVELS);
  if (r in LEVELS) {
    const [lo, hi, def] = LEVELS[r];
    ui.level.min = lo; ui.level.max = hi; ui.level.step = (hi - lo) / 40;
    if (!ui.level.dataset.rule || ui.level.dataset.rule !== r) { ui.level.value = def; ui.level.dataset.rule = r; }
    ui.levelOut.textContent = Number(ui.level.value).toFixed(2);
  }
}
ui.rule.addEventListener("change", syncLevel);
ui.level.addEventListener("input", syncLevel);
syncLevel();

const worker = new Worker(new URL("./worker.js", import.meta.url), { type: "module" });
worker.onmessage = ({ data }) => {
  if (!state) return;
  if (data.type === "gen") state.queue.push(data);
  else state.final = data;
};

ui.run.addEventListener("click", () => {
  const skew = Number(ui.skew.value);
  state = { skew, queue: [], shown: null, series: [], final: null, last: 0, scored: false,
    seed: Math.floor(Math.random() * 1e6) };
  ui.score.hidden = true;
  ui.run.disabled = true;
  worker.postMessage({ rule: ui.rule.value, level: Number(ui.level.value), skew, seed: state.seed,
    honest: ui.honest.checked });
});

// ---- drawing ----------------------------------------------------------------

const INK = "#1d1c17", PAPER = "#ecebe7", BLUE = "#2456d6", RED = "#d8361f";

function fitCanvas(c) {
  const r = c.getBoundingClientRect(), d = window.devicePixelRatio || 1;
  if (c.width !== Math.round(r.width * d)) { c.width = Math.round(r.width * d); c.height = Math.round(r.height * d); }
  const ctx = c.getContext("2d");
  ctx.setTransform(d, 0, 0, d, 0, 0);
  return { ctx, w: r.width, h: r.height };
}

function positions(n, w, h) {
  const R = Math.min(w, h) * 0.34, cx = w / 2, cy = h / 2;
  return Array.from({ length: n }, (_, i) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    return [cx + R * Math.cos(a), cy + R * Math.sin(a)];
  });
}

function wire(ctx, a, b, w, h, bend) {
  const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
  const cx = w / 2 + (mx - w / 2) * bend, cy = h / 2 + (my - h / 2) * bend;
  ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.quadraticCurveTo(cx, cy, b[0], b[1]); ctx.stroke();
}

function face(ctx, x, y, size, mood) {
  ctx.fillStyle = INK; ctx.strokeStyle = INK; ctx.lineWidth = Math.max(2, size * 0.05); ctx.lineCap = "round";
  const e = size * 0.14, ey = y - size * 0.08, ex = size * 0.17;
  if (mood === "smug") {
    for (const sx of [-1, 1]) { ctx.beginPath(); ctx.arc(x + sx * ex, ey + e * 0.6, e * 0.7, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke(); }
    ctx.beginPath(); ctx.arc(x, y + size * 0.1, size * 0.16, Math.PI * 0.15, Math.PI * 0.85); ctx.stroke();
  } else if (mood === "panic") {
    for (const sx of [-1, 1]) { ctx.beginPath(); ctx.arc(x + sx * ex, ey, e * 0.9, 0, 7); ctx.stroke(); ctx.beginPath(); ctx.arc(x + sx * ex, ey, e * 0.3, 0, 7); ctx.fill(); }
    ctx.beginPath(); ctx.ellipse(x, y + size * 0.2, size * 0.08, size * 0.11, 0, 0, 7); ctx.fill();
  } else {
    for (const sx of [-1, 1]) { ctx.beginPath(); ctx.arc(x + sx * ex, ey, e * 0.45, 0, 7); ctx.fill(); }
    ctx.beginPath(); ctx.moveTo(x - size * 0.12, y + size * 0.18); ctx.lineTo(x + size * 0.12, y + size * 0.18); ctx.stroke();
  }
}

function drawBoard(profile, m, skew, xray) {
  const { ctx, w, h } = fitCanvas(ui.board);
  ctx.clearRect(0, 0, w, h);
  const n = profile.length, pos = positions(n, w, h);
  const expo = exposure(config({ exposure_skew: skew }));
  const size = Math.min(w, h) * 0.13;
  // wires: each agent's coupling, visible ones on the surface, hidden ones underneath
  profile.forEach(([s, hidShare], i) => {
    const count = Math.round(s * 5);
    const hidden = Math.round(count * hidShare);
    for (let k = 0; k < count; k++) {
      const j = (i + 1 + (k % (n - 1))) % n;
      const isHidden = k < hidden;
      if (isHidden && !xray) continue;
      ctx.strokeStyle = isHidden ? RED : INK;
      ctx.globalAlpha = isHidden ? 0.75 : 0.55;
      ctx.lineWidth = isHidden ? 2 : 2.5;
      ctx.setLineDash(isHidden ? [6, 6] : []);
      wire(ctx, pos[i], pos[j], w, h, 0.15 + 0.12 * (k % 3));
    }
  });
  ctx.setLineDash([]); ctx.globalAlpha = 1;
  // modules
  const maxLoss = Math.max(0.06, ...m.perAgent);
  profile.forEach(([s, hidShare, q], i) => {
    const [x, y] = pos[i];
    const heat = Math.min(1, m.perAgent[i] / maxLoss);
    const mood = m.perAgent[i] > 0.09 ? "panic" : s > 0.62 ? "smug" : "calm";
    ctx.fillStyle = PAPER; ctx.strokeStyle = INK; ctx.lineWidth = 2;
    ctx.beginPath(); ctx.roundRect(x - size / 2, y - size / 2, size, size, size * 0.22); ctx.fill();
    ctx.globalAlpha = 0.15 + 0.7 * heat * heat; ctx.fillStyle = RED;
    ctx.beginPath(); ctx.roundRect(x - size / 2, y - size / 2, size, size, size * 0.22); ctx.fill();
    ctx.globalAlpha = 1; ctx.stroke();
    face(ctx, x, y, size, mood);
    // shortcut, hidden and testing levels as three short bars
    const bw = size * 0.9, by = y + size / 2 + 10;
    [["cut", s, INK], ["hid", hidShare, RED], ["test", q, BLUE]].forEach(([label, v, col], r) => {
      ctx.fillStyle = "#d3d2ce"; ctx.fillRect(x - bw / 2, by + r * 11, bw, 6);
      ctx.fillStyle = col; ctx.fillRect(x - bw / 2, by + r * 11, bw * v, 6);
    });
    ctx.fillStyle = INK; ctx.font = "12px system-ui"; ctx.textAlign = "center";
    if (skew > 0) ctx.fillText(`${Math.round(expo[i] / n * 100)}% of incidents`, x, y - size / 2 - 8);
  });
}

function drawSeries(canvas, values, color, lo, hi, refs = []) {
  const { ctx, w, h } = fitCanvas(canvas);
  ctx.clearRect(0, 0, w, h);
  const X = (g) => 4 + (g / 40) * (w - 8), Y = (v) => h - 4 - ((v - lo) / (hi - lo)) * (h - 8);
  for (const [v, col] of refs) {
    ctx.strokeStyle = col; ctx.globalAlpha = 0.6; ctx.setLineDash([4, 4]); ctx.lineWidth = 1.5;
    ctx.beginPath(); ctx.moveTo(4, Y(v)); ctx.lineTo(w - 4, Y(v)); ctx.stroke();
  }
  ctx.setLineDash([]); ctx.globalAlpha = 1; ctx.strokeStyle = color; ctx.lineWidth = 3;
  ctx.beginPath();
  values.forEach((v, g) => (g ? ctx.lineTo(X(g), Y(v)) : ctx.moveTo(X(g), Y(v))));
  ctx.stroke();
}

function score() {
  const ref = REFERENCE[state.skew], got = state.final.systemCost;
  const closed = (ref.nothing - got) / (ref.nothing - ref.best);
  const hidden = Math.round(state.final.hiddenShare * 100);
  let big, line;
  if (closed < 0) {
    const worse = Math.round(((got - ref.nothing) / ref.nothing) * 100);
    big = `${worse}% worse`;
    line = `Your rule backfired: the system now costs ${worse}% more than if you had done nothing.`;
  } else {
    const pts = Math.min(100, Math.round(closed * 100));
    big = `${pts} / 100`;
    line = pts >= 90 ? "Close to the best possible. Very hard to beat."
      : pts >= 50 ? "Better than nothing, but they found room to slip."
      : "They mostly got around your rule.";
  }
  if (hidden >= 50) line += ` They hid ${hidden}% of their coupling; switch on X-ray to see it.`;
  ui.score.innerHTML = `<b>${big}</b>${line}<span>System cost ${got.toFixed(4)}: doing nothing ${ref.nothing}, best possible ${ref.best}. 100 means you matched the best possible outcome.</span>`;
  ui.score.hidden = false;
  ui.run.disabled = false;
}

function frame() {
  const t = performance.now();
  if (state) {
    const perGen = 1000 / Number(ui.speed.value);
    if (state.queue.length && t - state.last > perGen) {
      const g = state.queue.shift();
      state.shown = g;
      state.last = t;
      const m = metrics(g.profile, state.skew);
      state.metrics = m;
      state.series.push(m);
      ui.gen.textContent = `Generation ${Math.min(g.gen, 40)} of 40`;
    }
    if (state.shown) {
      drawBoard(state.shown.profile, state.metrics, state.skew, ui.xray.checked);
      const ref = REFERENCE[state.skew];
      drawSeries(ui.cost, state.series.map((m) => m.cost), INK, ref.best - 0.03, 0.42,
        [[ref.nothing, INK], [ref.best, BLUE]]);
      drawSeries(ui.hid, state.series.map((m) => m.hidden), RED, 0, 1);
    }
    if (state.final && !state.queue.length && !state.scored) { state.scored = true; score(); }
  }
  setTimeout(frame, 16);
}
frame();
window.__debug = () => state && { queue: state.queue.length, shown: state.shown && state.shown.gen, final: !!state.final };
worker.onerror = (e) => console.error("worker error", e.message, e.filename, e.lineno);
