// "Try to stop them": the agents run continuously; you change the rule whenever
// you like and watch them adapt. Everything on the board is driven by the real
// engine: wires are each agent's coupling, red sparks are its modelled incident
// losses, the tide is the shared debt.
import { config, simulate, exposure } from "../engine/model.js";
import { makeBatch } from "../engine/scenarios.js";

const COL = { ink: "#1d1c17", paper: "#f7f5f0", card: "#ecebe7", blue: "#2456d6", red: "#d8361f",
  tide: "#2456d6", shadow: "rgba(29,28,23,0.10)" };
const DIAL = { visible: { lo: 0.05, hi: 0.8, def: 0.4 }, damage: { lo: 0.25, hi: 2, def: 1 } };
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
const $ = (s) => document.querySelector(s);
const board = $("#board");

// ---- the model on a small fixed batch, for what the board shows --------------

const vis = {};
function visFor(skew) {
  if (!vis[skew]) {
    const cfg = config({ exposure_skew: skew });
    const b = makeBatch(cfg, "base", "site", 0, 12);
    const cost = (P) => {
      const o = simulate(b, P, cfg);
      let c = 0;
      for (let s = 0; s < b.S; s++) { let x = 0; for (let i = 0; i < cfg.n; i++) x += o.cost[s * cfg.n + i]; c += x / o.nominal[s]; }
      return c / b.S;
    };
    // Reference points on the same scenarios: agents left alone settle near
    // s = 0.97, q = 0.97 (E9); the best outcome is searched on a grid, then
    // per agent when exposure is unequal.
    const nothing = cost(Array(cfg.n).fill([0.97, 0, 0.97]));
    let best = [0.5, 0, 0], bc = Infinity;
    for (let si = 0; si <= 20; si++) for (const q of [0, 0.25, 0.5]) {
      const s = si / 20;
      const c = cost(Array(cfg.n).fill([s, 0, q]));
      if (c < bc) { bc = c; best = [s, 0, q]; }
    }
    let P = Array(cfg.n).fill(best);
    if (skew > 0) for (let sweep = 0; sweep < 2; sweep++) for (let i = 0; i < cfg.n; i++) {
      for (let si = 0; si <= 20; si++) for (const q of [0, 0.25, 0.5, 0.75]) {
        const s = si / 20;
        const Q = P.map((p, j) => (j === i ? [s, 0, q] : p));
        const c = cost(Q);
        if (c < bc) { bc = c; P = Q; }
      }
    }
    vis[skew] = { cfg, b, nothing, best: bc, expo: exposure(cfg) };
  }
  return vis[skew];
}

function measure(profile, skew) {
  const { cfg, b } = visFor(skew);
  const o = simulate(b, profile, cfg);
  const n = cfg.n, hits = new Array(n).fill(0);
  let cost = 0, v = 0, h = 0, debt = 0;
  for (let s = 0; s < b.S; s++) {
    let c = 0;
    for (let i = 0; i < n; i++) {
      c += o.cost[s * n + i];
      hits[i] += o.charges[(s * n + i) * 4 + 2] / o.nominal[s] * n / b.S;
    }
    cost += c / o.nominal[s] / b.S;
    v += o.visible[s]; h += o.hidden[s]; debt += o.debt[s] / b.S;
  }
  return { hits, cost, hidden: v + h > 0 ? h / (v + h) : 0, debt };
}

// ---- state --------------------------------------------------------------------

const S = {
  rule: "visible", level: DIAL.visible.def, skew: 0, honest: true, xray: false, speed: 3,
  running: false, job: 0, gen: 0, seed: 1, queue: [], pending: false, lastQueued: null,
  from: null, to: null, tStart: 0, m: null, gauge: 0, gaugeV: 0, series: [], said: new Set(),
  sparks: [], ripples: [], shake: [0, 0, 0, 0, 0, 0], ropes: new Map(), chunks: 0,
};

const worker = new Worker(new URL("./worker.js", import.meta.url), { type: "module" });
worker.onmessage = ({ data }) => {
  if (data.job !== S.job) return;
  if (data.chunkDone) { S.pending = false; return; }
  S.queue.push(data.profile);
  S.lastQueued = data.profile;
};

function request(init) {
  S.pending = true;
  S.chunks += 1;
  worker.postMessage({ job: S.job, rule: S.rule, level: S.level, skew: S.skew, seed: S.seed,
    honest: S.honest, init, gens: 8, genOffset: S.chunks * 101 });
}

function freshAgents() {
  S.job += 1; S.queue = []; S.gen = 0; S.series = []; S.said.clear(); S.seed = Math.floor(Math.random() * 1e6);
  S.from = S.to = null; S.lastQueued = null; S.sparks = []; S.ripples = [];
  request(null);
}

// a rule change keeps the agents where they are and lets them adapt
function changeRule() {
  if (!S.to) return freshAgents();
  S.job += 1; S.queue = []; S.lastQueued = S.to;
  request(S.to);
  say(RULE_TEXT[S.rule].said);
}

// ---- controls -----------------------------------------------------------------

const RULE_TEXT = {
  none: { said: "No rule. Every agent keeps whatever helps itself." },
  conscience: { said: "Each agent now asks: what if everyone made my change?" },
  visible: { said: "Every shortcut you can see now costs its author." },
  damage: { said: "Each agent now pays for the damage that lands on everyone else." },
};

document.querySelectorAll("[data-rule]").forEach((btn) => btn.addEventListener("click", () => {
  if (S.rule === btn.dataset.rule) return;
  S.rule = btn.dataset.rule;
  document.querySelectorAll("[data-rule]").forEach((b) => b.setAttribute("aria-pressed", b === btn));
  const d = DIAL[S.rule];
  $("#dial").classList.toggle("off", !d);
  if (d) setLevel(d.def);
  changeRule();
}));

document.querySelectorAll("[data-skew]").forEach((btn) => btn.addEventListener("click", () => {
  S.skew = Number(btn.dataset.skew);
  document.querySelectorAll("[data-skew]").forEach((b) => b.setAttribute("aria-pressed", b === btn));
  visFor(S.skew);
  freshAgents();
}));

$("#play").addEventListener("click", () => {
  S.running = !S.running;
  $("#play").textContent = S.running ? "Pause" : "Run";
  $("#play").setAttribute("aria-pressed", S.running);
  if (S.running && !S.to && !S.pending) freshAgents();
});
$("#reset").addEventListener("click", () => { freshAgents(); say("Six new agents. Honest, for now."); });
$("#xray").addEventListener("click", () => {
  S.xray = !S.xray;
  $("#xray").setAttribute("aria-pressed", S.xray);
  board.classList.toggle("xray", S.xray);
});
document.querySelectorAll("[data-speed]").forEach((btn) => btn.addEventListener("click", () => {
  S.speed = Number(btn.dataset.speed);
  document.querySelectorAll("[data-speed]").forEach((b) => b.setAttribute("aria-pressed", b === btn));
}));

// The dial: drag round it, or use the arrow keys.
const knob = $("#knob"), dialVal = $("#dialVal");
function setLevel(v) {
  const d = DIAL[S.rule];
  if (!d) return;
  S.level = Math.min(d.hi, Math.max(d.lo, v));
  const f = (S.level - d.lo) / (d.hi - d.lo);
  knob.style.setProperty("--turn", `${-135 + 270 * f}deg`);
  knob.setAttribute("aria-valuenow", S.level.toFixed(2));
  knob.setAttribute("aria-valuemin", d.lo);
  knob.setAttribute("aria-valuemax", d.hi);
  dialVal.textContent = S.level.toFixed(2);
}
let dialTimer = null;
function levelChanged() { clearTimeout(dialTimer); dialTimer = setTimeout(() => { if (S.to) changeRule(); }, 250); }
knob.addEventListener("pointerdown", (e) => {
  knob.setPointerCapture(e.pointerId);
  const move = (ev) => {
    const r = knob.getBoundingClientRect();
    let a = Math.atan2(ev.clientX - (r.left + r.width / 2), -(ev.clientY - (r.top + r.height / 2))) * 180 / Math.PI;
    a = Math.max(-135, Math.min(135, a));
    const d = DIAL[S.rule];
    setLevel(d.lo + ((a + 135) / 270) * (d.hi - d.lo));
  };
  move(e);
  knob.onpointermove = move;
  knob.onpointerup = () => { knob.onpointermove = null; levelChanged(); };
});
knob.addEventListener("keydown", (e) => {
  const d = DIAL[S.rule]; if (!d) return;
  const step = (d.hi - d.lo) / 20;
  if (["ArrowRight", "ArrowUp"].includes(e.key)) { setLevel(S.level + step); levelChanged(); e.preventDefault(); }
  if (["ArrowLeft", "ArrowDown"].includes(e.key)) { setLevel(S.level - step); levelChanged(); e.preventDefault(); }
});
setLevel(S.level);

// narration, one line at a time
let sayTimer = null;
function say(text) {
  const el = $("#say");
  el.classList.remove("in");
  void el.offsetWidth;
  el.textContent = text;
  el.classList.add("in");
  clearTimeout(sayTimer);
  sayTimer = setTimeout(() => el.classList.remove("in"), 4200);
}
function sayOnce(key, text) { if (!S.said.has(key)) { S.said.add(key); say(text); } }

// ---- drawing --------------------------------------------------------------------

function fit(c) {
  const r = c.getBoundingClientRect(), d = Math.min(2, window.devicePixelRatio || 1);
  if (c.width !== Math.round(r.width * d) || c.height !== Math.round(r.height * d)) {
    c.width = Math.round(r.width * d); c.height = Math.round(r.height * d);
  }
  const ctx = c.getContext("2d");
  ctx.setTransform(d, 0, 0, d, 0, 0);
  return { ctx, w: r.width, h: r.height };
}

const ease = (x) => (x < 0.5 ? 4 * x * x * x : 1 - (-2 * x + 2) ** 3 / 2);
const lerpProfile = (a, b, f) => a.map((p, i) => p.map((x, k) => x + (b[i][k] - x) * f));

function layout(n, w, h) {
  const R = Math.min(w * 0.38, h * 0.36), cx = w / 2, cy = h * 0.47;
  return Array.from({ length: n }, (_, i) => {
    const a = -Math.PI / 2 + (i * 2 * Math.PI) / n;
    return [cx + R * Math.cos(a), cy + R * Math.sin(a)];
  });
}

// wire control points are little masses on springs: they sway, and shake more
// as the shared debt rises
function rope(key, rest, tension, dt) {
  let r = S.ropes.get(key);
  if (!r) { r = { x: rest[0], y: rest[1], vx: 0, vy: 0 }; S.ropes.set(key, r); }
  const k = 18 + 30 * tension, damp = 4.5;
  const jitter = REDUCED ? 0 : (8 + 60 * tension);
  r.vx += (k * (rest[0] - r.x) - damp * r.vx + (Math.random() - 0.5) * jitter * 6) * dt;
  r.vy += (k * (rest[1] - r.y) - damp * r.vy + (Math.random() - 0.5) * jitter * 6) * dt;
  r.x += r.vx * dt; r.y += r.vy * dt;
  return r;
}

function quadPoint(a, c, b, t) {
  const u = 1 - t;
  return [u * u * a[0] + 2 * u * t * c[0] + t * t * b[0], u * u * a[1] + 2 * u * t * c[1] + t * t * b[1]];
}

function wiresOf(P, pos, w, h, tension, dt) {
  const n = P.length, out = [];
  P.forEach(([s, m], i) => {
    const count = s * 5, hiddenCount = m * count;
    for (let k = 0; k < 5; k++) {
      const present = Math.max(0, Math.min(1, count - k));
      if (present <= 0) continue;
      const hid = Math.max(0, Math.min(1, hiddenCount - k));
      const j = (i + 1 + (k % (n - 1))) % n;
      const a = pos[i], b = pos[j];
      const mx = (a[0] + b[0]) / 2, my = (a[1] + b[1]) / 2;
      const bend = 0.12 + 0.13 * (k % 3);
      const rest = [w / 2 + (mx - w / 2) * bend + (k - 2) * 6, h * 0.47 + (my - h * 0.47) * bend + (i - 2.5) * 4];
      const c = rope(`${i}-${k}`, rest, tension, dt);
      out.push({ i, j, a, b, c: [c.x, c.y], present, hid });
    }
  });
  return out;
}

function face(ctx, x, y, size, mood, blink) {
  ctx.fillStyle = COL.ink; ctx.strokeStyle = COL.ink; ctx.lineCap = "round"; ctx.lineWidth = Math.max(2, size * 0.055);
  const ex = size * 0.18, ey = y - size * 0.08, e = size * 0.07;
  if (mood === "panic") {
    for (const sx of [-1, 1]) {
      ctx.beginPath(); ctx.arc(x + sx * ex, ey, e * 1.5, 0, 7); ctx.stroke();
      ctx.beginPath(); ctx.arc(x + sx * ex, ey, e * 0.55, 0, 7); ctx.fill();
    }
    ctx.beginPath(); ctx.ellipse(x, y + size * 0.21, size * 0.08, size * 0.11, 0, 0, 7); ctx.fill();
  } else if (mood === "smug") {
    for (const sx of [-1, 1]) { ctx.beginPath(); ctx.arc(x + sx * ex, ey + e, e * 1.2, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke(); }
    ctx.beginPath(); ctx.arc(x + size * 0.03, y + size * 0.08, size * 0.17, Math.PI * 0.12, Math.PI * 0.8); ctx.stroke();
  } else {
    for (const sx of [-1, 1]) {
      if (blink) { ctx.beginPath(); ctx.moveTo(x + sx * ex - e, ey); ctx.lineTo(x + sx * ex + e, ey); ctx.stroke(); }
      else { ctx.beginPath(); ctx.arc(x + sx * ex, ey, e, 0, 7); ctx.fill(); }
    }
    ctx.beginPath(); ctx.moveTo(x - size * 0.11, y + size * 0.19); ctx.lineTo(x + size * 0.11, y + size * 0.19); ctx.stroke();
  }
}

let lastT = performance.now();
function frame() {
  const t = performance.now();
  const dt = Math.min(0.05, (t - lastT) / 1000);
  lastT = t;
  const genMs = 1000 / S.speed;

  // advance one generation
  if (S.running && S.queue.length && (!S.to || t - S.tStart >= genMs)) {
    S.from = S.to || S.queue[0];
    S.to = S.queue.shift();
    S.tStart = t;
    S.gen += 1;
    S.m = measure(S.to, S.skew);
    S.series.push({ cost: S.m.cost, hidden: S.m.hidden });
    if (S.series.length > 80) S.series.shift();
    // incidents for this generation: each module gets sparks in proportion to
    // its modelled incident loss, spread over the generation
    // (about 1.5 per second per module at a typical incident level, whatever the speed)
    S.m.hits.forEach((x, i) => {
      let lam = (x / 0.1) * 1.5 * (genMs / 1000), k = 0, p = Math.exp(-lam), c = p;
      const u = Math.random();
      while (u > c && k < 6) { k += 1; p *= lam / k; c += p; }
      for (let e = 0; e < k; e++) S.sparks.push({ at: t + Math.random() * genMs * 0.9, i, src: (i + 1 + Math.floor(Math.random() * 5)) % 6 });
    });
    narrate();
  }
  if (S.running && !S.pending && S.queue.length < 4 && S.lastQueued) request(S.lastQueued);

  draw(t, dt, genMs);
  drawGauge(dt);
  drawSpark($("#costLine"), S.series.map((x) => x.cost), COL.ink);
  drawSpark($("#hidLine"), S.series.map((x) => x.hidden), COL.red, 0, 1);
  $("#genNo").textContent = S.gen;
  setTimeout(frame, 16);
}

function draw(t, dt, genMs) {
  const { ctx, w, h } = fit(board);
  ctx.clearRect(0, 0, w, h);
  const P = S.to ? lerpProfile(S.from || S.to, S.to, ease(Math.min(1, (t - S.tStart) / genMs)))
    : Array(6).fill([0.4, 0, 0.1]);
  const pos = layout(6, w, h);
  const debt = S.m ? S.m.debt : 0.3;
  const tension = Math.min(1, debt / 4);
  const size = Math.min(w, h) * 0.135;

  // debt tide
  // shared debt as a tide: about a quarter of the board at the best outcome,
  // over half when coupling has gone underground
  S.tide = S.tide ?? 0;
  S.tide += ((0.03 + Math.min(0.55, debt * 0.085)) - S.tide) * Math.min(1, dt * 2.5);
  const tideH = h * S.tide;
  ctx.fillStyle = COL.tide; ctx.globalAlpha = 0.16;
  ctx.beginPath(); ctx.moveTo(0, h);
  for (let x = 0; x <= w; x += 8) ctx.lineTo(x, h - tideH + Math.sin(x / 38 + t / 700) * 6 + Math.sin(x / 17 - t / 430) * 3);
  ctx.lineTo(w, h); ctx.fill(); ctx.globalAlpha = 1;
  ctx.fillStyle = COL.blue; ctx.font = "600 13px Jost, system-ui"; ctx.textAlign = "left";
  ctx.fillText("Shared debt", 18, h - tideH - 12);

  const wires = wiresOf(P, pos, w, h, tension, dt);
  // hidden coupling: under the paper. A faint shadow normally; with X-ray, red.
  for (const wr of wires) {
    if (wr.hid <= 0) continue;
    ctx.save();
    if (S.xray) { ctx.strokeStyle = COL.red; ctx.globalAlpha = 0.85 * wr.hid * wr.present; ctx.setLineDash([7, 6]); ctx.lineDashOffset = -t / 40; ctx.lineWidth = 2.2; }
    else { ctx.strokeStyle = COL.ink; ctx.globalAlpha = 0.06 * wr.hid * wr.present; ctx.lineWidth = 6; }
    ctx.beginPath(); ctx.moveTo(...wr.a); ctx.quadraticCurveTo(...wr.c, ...wr.b); ctx.stroke();
    ctx.restore();
  }
  // visible coupling
  for (const wr of wires) {
    const a = wr.present * (1 - wr.hid);
    if (a <= 0.01) continue;
    ctx.strokeStyle = COL.ink; ctx.globalAlpha = 0.6 * a; ctx.lineWidth = 2.4;
    ctx.beginPath(); ctx.moveTo(...wr.a); ctx.quadraticCurveTo(...wr.c, ...wr.b); ctx.stroke();
  }
  ctx.globalAlpha = 1;

  // sparks: run along a wire into the module they hit
  S.sparks = S.sparks.filter((sp) => {
    if (t < sp.at) return true;
    const p = Math.min(1, (t - sp.at) / 380);
    const wr = wires.find((x) => (x.i === sp.src && x.j === sp.i) || (x.i === sp.i && x.j === sp.src));
    const a = pos[sp.src], b = pos[sp.i];
    const c = wr ? wr.c : [(a[0] + b[0]) / 2, (a[1] + b[1]) / 2];
    const q = wr && wr.i !== sp.src ? quadPoint(b, c, a, 1 - p) : quadPoint(a, c, b, p);
    ctx.fillStyle = COL.red; ctx.globalAlpha = 1;
    ctx.beginPath(); ctx.arc(q[0], q[1], 5, 0, 7); ctx.fill();
    ctx.globalAlpha = 0.25; ctx.beginPath(); ctx.arc(q[0], q[1], 11, 0, 7); ctx.fill(); ctx.globalAlpha = 1;
    if (p >= 1) {
      S.ripples = S.ripples.filter((r) => r.i !== sp.i);
      S.ripples.push({ i: sp.i, t0: t });
      S.shake[sp.i] = REDUCED ? 0 : 1;
      return false;
    }
    return true;
  });

  // ripples
  S.ripples = S.ripples.filter((rp) => {
    const p = (t - rp.t0) / 520;
    if (p >= 1) return false;
    const [x, y] = pos[rp.i];
    ctx.strokeStyle = COL.red; ctx.globalAlpha = 0.7 * (1 - p); ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(x, y, size * (0.62 + p * 0.7), 0, 7); ctx.stroke();
    ctx.globalAlpha = 1;
    return true;
  });

  // modules
  const { expo } = visFor(S.skew);
  P.forEach(([s, m, q], i) => {
    const hit = S.m ? S.m.hits[i] : 0;
    const recent = S.ripples.some((rp) => rp.i === i && t - rp.t0 < 350);
    const mood = recent ? "panic" : s > 0.6 ? "smug" : "calm";
    S.shake[i] *= Math.exp(-dt * 9);
    const sh = S.shake[i] * 6;
    const breathe = REDUCED ? 1 : 1 + 0.025 * Math.sin(t / 650 + i * 1.3);
    const sz = size * breathe * (S.skew > 0 ? 0.85 + 0.35 * Math.sqrt(expo[i] / 6 * 2) : 1);
    const x = pos[i][0] + (Math.random() - 0.5) * sh, y = pos[i][1] + (Math.random() - 0.5) * sh;
    // shadow, body, heat, armour (testing)
    ctx.fillStyle = COL.shadow;
    ctx.beginPath(); ctx.roundRect(x - sz / 2 + 4, y - sz / 2 + 6, sz, sz, sz * 0.24); ctx.fill();
    ctx.fillStyle = "#fff";
    ctx.beginPath(); ctx.roundRect(x - sz / 2, y - sz / 2, sz, sz, sz * 0.24); ctx.fill();
    const heat = Math.min(1, hit / 0.3) * 0.3 + (recent ? 0.45 : 0);
    ctx.fillStyle = COL.red; ctx.globalAlpha = heat;
    ctx.beginPath(); ctx.roundRect(x - sz / 2, y - sz / 2, sz, sz, sz * 0.24); ctx.fill();
    ctx.globalAlpha = 1;
    ctx.strokeStyle = COL.blue; ctx.lineWidth = 2 + q * 6;
    ctx.globalAlpha = 0.25 + 0.75 * q;
    ctx.beginPath(); ctx.roundRect(x - sz / 2, y - sz / 2, sz, sz, sz * 0.24); ctx.stroke();
    ctx.globalAlpha = 1;
    const blink = !REDUCED && ((t / 1000 + i * 0.77) % 4.2) < 0.12;
    face(ctx, x, y, sz, mood, blink);
    if (S.skew > 0) {
      ctx.fillStyle = COL.ink; ctx.font = "600 13px Jost, system-ui"; ctx.textAlign = "center";
      ctx.fillText(`${Math.round(expo[i] / 6 * 100)}% of incidents`, x, y - sz / 2 - 10);
    }
  });
}

// the gauge swings between worse than nothing, nothing, and the best possible
function drawGauge(dt) {
  const c = $("#gauge");
  const { ctx, w, h } = fit(c);
  ctx.clearRect(0, 0, w, h);
  let target = 0;
  if (S.m) {
    const v = visFor(S.skew);
    target = Math.max(-1, Math.min(1.05, (v.nothing - S.m.cost) / (v.nothing - v.best)));
  }
  S.gaugeV += (60 * (target - S.gauge) - 9 * S.gaugeV) * dt;
  S.gauge += S.gaugeV * dt;
  const cx = w / 2, cy = h * 0.92, R = Math.min(w / 2 - 12, h * 0.82);
  const ang = (g) => Math.PI + ((g + 1) / 2.05) * Math.PI;
  const arc = (a0, a1, col) => { ctx.strokeStyle = col; ctx.lineWidth = 14; ctx.beginPath(); ctx.arc(cx, cy, R, ang(a0), ang(a1)); ctx.stroke(); };
  arc(-1, 0, "rgba(216,54,31,0.35)"); arc(0, 1.05, "rgba(36,86,214,0.35)");
  const a = ang(S.gauge);
  ctx.strokeStyle = COL.ink; ctx.lineWidth = 4; ctx.lineCap = "round";
  ctx.beginPath(); ctx.moveTo(cx, cy); ctx.lineTo(cx + Math.cos(a) * (R - 6), cy + Math.sin(a) * (R - 6)); ctx.stroke();
  ctx.fillStyle = COL.ink; ctx.beginPath(); ctx.arc(cx, cy, 7, 0, 7); ctx.fill();
  let label = "–";
  if (S.m) {
    const v = visFor(S.skew);
    label = S.m.cost > v.nothing
      ? `${Math.round(((S.m.cost - v.nothing) / v.nothing) * 100)}% worse`
      : `${Math.round(Math.min(1, Math.max(0, S.gauge)) * 100)} / 100`;
  }
  $("#gaugeNo").textContent = label;
}

function drawSpark(c, vals, col, lo, hi) {
  const { ctx, w, h } = fit(c);
  ctx.clearRect(0, 0, w, h);
  if (vals.length < 2) return;
  const mn = lo ?? Math.min(...vals) - 0.005, mx = hi ?? Math.max(...vals) + 0.005;
  ctx.strokeStyle = col; ctx.lineWidth = 2.5; ctx.lineJoin = "round";
  ctx.beginPath();
  vals.forEach((v, i) => {
    const x = (i / 79) * w, y = h - 3 - ((v - mn) / (mx - mn || 1)) * (h - 6);
    i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
  });
  ctx.stroke();
}

function narrate() {
  const m = S.m;
  if (m.hidden > 0.5 && !S.xray) sayOnce("hide", "They are hiding their coupling. Switch on X-ray.");
  if (S.rule === "visible" && m.hidden > 0.8) sayOnce("hide2", "Tax what you can see, and they stop letting you see it.");
  if (S.rule === "conscience" && S.skew > 0 && S.gen > 12) sayOnce("cons", "Watch the busiest module: its conscience makes it freeze while the quiet ones run wild.");
  const v = visFor(S.skew);
  if ((v.nothing - m.cost) / (v.nothing - v.best) > 0.9 && S.gen > 8) sayOnce("good", "Close to the best possible. Can you find anything better?");
}

visFor(0);
window.__debug = () => ({ gen: S.gen, queue: S.queue.length, running: S.running, gauge: S.gauge, m: S.m && { cost: S.m.cost, hidden: S.m.hidden } });
frame();
