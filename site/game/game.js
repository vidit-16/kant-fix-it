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

// "Doing nothing" and "best possible" on the board's 12 scenarios, from
// `node site/game/calibrate.mjs --refs` (selfish agents' settling cost, and the
// best profile found from every rule's runs, polished by coordinate descent).
const REF = {"0": {"nothing": 0.21592, "best": 0.16997}, "0.75": {"nothing": 0.19458, "best": 0.16385}, "1.5": {"nothing": 0.16342, "best": 0.14541}};

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
        vis[skew] = { cfg, b, cost, expo: exposure(cfg) };
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
  step: null, focus: null, pos: null, size: 0, lvl: 0, hold: 0, lvlGen: 0, won: false, lost: false, hinted: false, celebrate: 0,
};

const worker = new Worker(new URL("./worker.js", import.meta.url), { type: "module" });
worker.onmessage = ({ data }) => {
  if (data.job !== S.job) return;
  if (data.chunkDone) { S.pending = false; return; }
  S.queue.push(data);
  S.lastQueued = data.profile;
};

function request(init) {
  S.pending = true;
  S.chunks += 1;
  worker.postMessage({ job: S.job, rule: S.rule, level: S.level, skew: S.skew, seed: S.seed,
    honest: S.honest, init, gens: 8, genOffset: S.chunks * 101 });
}

function freshAgents(init = null) {
  S.job += 1; S.queue = []; S.gen = 0; S.series = []; S.said.clear(); S.seed = Math.floor(Math.random() * 1e6);
  S.from = S.to = null; S.lastQueued = null; S.sparks = []; S.ripples = []; S.step = null;
  request(init);
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
  if (btn.disabled || S.rule === btn.dataset.rule) return;
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
  if (S.running && !S.to && !S.pending) freshAgents(LEVELS[S.lvl].init ?? null);
  if (S.running && (S.won || S.lost) && !LEVELS[S.lvl].free && $("#result").hidden === false) $("#result").hidden = true;
  $("#start").classList.add("gone");
});
$("#reset").addEventListener("click", () => loadLevel(S.lvl));
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

// the ring leaves room for the largest module, its ripple and its label
function layout(n, w, h, size) {
  const pad = size * 1.4 + 22;
  const R = Math.max(40, Math.min(w / 2 - pad, h / 2 - pad)), cx = w / 2, cy = h / 2;
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
      const rest = [w / 2 + (mx - w / 2) * bend + (k - 2) * 6, h / 2 + (my - h / 2) * bend + (i - 2.5) * 4];
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
  const genMs = S.focus !== null ? 2800 : 1000 / S.speed;

  // advance one generation
  if (S.running && S.queue.length && (!S.to || t - S.tStart >= genMs)) {
    const step = S.queue.shift();
    S.from = S.to || step.before;
    S.to = step.profile;
    S.step = step;
    S.tStart = t;
    if (S.focus !== null) explain(S.focus);
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
    levelTick();
    if (S.lvlGen === 4 && innerWidth < 900) sayOnce("tap", "Tap an agent to see what it is thinking.");
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
  const f = S.to ? Math.min(1, (t - S.tStart) / genMs) : 0;
  const thinking = !REDUCED && S.step && genMs >= 300;
  const fMove = thinking ? Math.max(0, Math.min(1, (f - 0.66) / 0.3)) : f;
  const P = S.to ? lerpProfile(S.from || S.to, S.to, ease(fMove)) : Array(6).fill([0.4, 0, 0.1]);
  const size = Math.min(w, h) * 0.12;
  const pos = layout(6, w, h, size);
  S.pos = pos; S.size = size;
  const debt = S.m ? S.m.debt : 0.3;
  const tension = Math.min(1, debt / 4);

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
  ctx.fillStyle = COL.blue; ctx.font = "600 13px \"Bricolage Grotesque\", system-ui"; ctx.textAlign = "left";
  ctx.fillText("Shared debt", 12, h - tideH - 10);

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

  if (S.celebrate && t - S.celebrate < 1800) {
    const p = (t - S.celebrate) / 1800;
    pos.forEach(([x, y]) => {
      for (const lag of [0, 0.18, 0.36]) {
        const q = p - lag; if (q <= 0 || q >= 1) continue;
        ctx.strokeStyle = COL.blue; ctx.globalAlpha = 0.6 * (1 - q); ctx.lineWidth = 4;
        ctx.beginPath(); ctx.arc(x, y, size * (0.7 + q * 1.6), 0, 7); ctx.stroke();
      }
    });
    ctx.globalAlpha = 1;
  }

  // ripples
  S.ripples = S.ripples.filter((rp) => {
    const p = (t - rp.t0) / 520;
    if (p >= 1) return false;
    const [x, y] = pos[rp.i];
    ctx.strokeStyle = COL.red; ctx.globalAlpha = 0.7 * (1 - p); ctx.lineWidth = 3;
    ctx.beginPath(); ctx.arc(x, y, size * (0.6 + p * 0.45), 0, 7); ctx.stroke();
    ctx.globalAlpha = 1;
    return true;
  });

  if (thinking) drawThinking(ctx, t, f, pos, size, w, h);

  // modules
  const { expo } = visFor(S.skew);
  P.forEach(([s, m, q], i) => {
    const hit = S.m ? S.m.hits[i] : 0;
    const recent = S.ripples.some((rp) => rp.i === i && t - rp.t0 < 350);
    const mood = recent ? "panic" : s > 0.6 ? "smug" : "calm";
    S.shake[i] *= Math.exp(-dt * 9);
    const sh = S.shake[i] * 6;
    const breathe = REDUCED ? 1 : 1 + 0.025 * Math.sin(t / 650 + i * 1.3);
    const sz = size * breathe * (S.skew > 0 ? 0.88 + 0.3 * Math.min(1, Math.sqrt(expo[i] / 6 * 2)) : 1);
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
    if (S.focus === i) {
      ctx.strokeStyle = COL.ink; ctx.lineWidth = 2; ctx.setLineDash([4, 5]);
      ctx.beginPath(); ctx.roundRect(x - sz / 2 - 9, y - sz / 2 - 9, sz + 18, sz + 18, sz * 0.3); ctx.stroke(); ctx.setLineDash([]);
    }
    if (S.skew > 0) {
      ctx.fillStyle = COL.ink; ctx.font = `600 ${w < 500 ? 11 : 13}px "Bricolage Grotesque", system-ui`; ctx.textAlign = "center";
      const oa = Math.atan2(pos[i][1] - h / 2, pos[i][0] - w / 2);
      ctx.textBaseline = "middle";
      ctx.fillText(w < 500 ? `${Math.round(expo[i] / 6 * 100)}%` : `${Math.round(expo[i] / 6 * 100)}% of incidents`,
        pos[i][0] + Math.cos(oa) * (size * 0.5 + 16), pos[i][1] + Math.sin(oa) * (size * 0.5 + 16));
      ctx.textBaseline = "alphabetic";
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
    target = Math.max(-1, Math.min(1.05, scoreOf(S.m.cost, S.skew) / 100));
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
    const v = REF[S.skew];
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
  if (scoreOf(m.cost, S.skew) > 90 && S.gen > 8) sayOnce("good", "Close to the best possible. Can you find anything better?");
}

// ---- watching them think ------------------------------------------------------
// Each generation every agent tries a few small changes to its own policy.
// Ghost copies show the candidates; the agent's rule stamps each one kept or
// rejected; the kept one slides in. Under the conscience rule, the focused
// agent's imagined board ("what if everyone did this?") fades over the real one.

const KIND = [["cut more corners", "cut fewer corners"], ["hide more coupling", "hide less coupling"], ["test more", "test less"]];
function describe(before, cand) {
  const d = cand.map((x, a) => x - before[a]);
  let a = 0;
  for (let k = 1; k < 3; k++) if (Math.abs(d[k]) > Math.abs(d[a])) a = k;
  return KIND[a][d[a] >= 0 ? 0 : 1];
}

function ghostSpot(pos, i, k, size, w, h) {
  const [x, y] = pos[i];
  const out = Math.atan2(y - h / 2, x - w / 2);
  const a = out + (k - 1.5) * 0.62;
  const r = size * 1.12;
  return [x + Math.cos(a) * r, y + Math.sin(a) * r];
}

function drawThinking(ctx, t, f, pos, size, w, h) {
  const dec = S.step.decisions;
  const g = size * 0.42;
  dec.forEach((d, i) => {
    if (!d) return;
    if (S.focus !== null && S.focus !== i) return;
    if (S.focus !== i) { decisionDots(ctx, f, d, pos, i, size, w, h); return; }
    d.candidates.forEach((c, k) => {
      const appear = 0.05 + k * 0.08;
      if (f < appear) return;
      const kept = d.chosen === k;
      let [gx, gy] = ghostSpot(pos, i, k, size * (S.focus === i ? 1.25 : 1), w, h);
      let alpha = Math.min(1, (f - appear) / 0.08) * 0.85;
      if (f > 0.62) {
        const m = Math.min(1, (f - 0.62) / 0.22);
        if (kept) { gx += (pos[i][0] - gx) * ease(m); gy += (pos[i][1] - gy) * ease(m); alpha *= 1 - m * 0.9; }
        else alpha *= 1 - m;
      }
      if (alpha <= 0.02) return;
      ctx.globalAlpha = alpha;
      ctx.fillStyle = "#ffffff"; ctx.strokeStyle = COL.ink; ctx.lineWidth = 1.5;
      if (c.policy[1] > 0.5) ctx.setLineDash([4, 3]);
      ctx.beginPath(); ctx.roundRect(gx - g / 2, gy - g / 2, g, g, g * 0.26); ctx.fill(); ctx.stroke();
      ctx.setLineDash([]);
      face(ctx, gx, gy, g, c.policy[0] > 0.6 ? "smug" : "calm", false);
      if (f > 0.4) {
        const st = Math.min(1, (f - 0.4) / 0.08);
        ctx.globalAlpha = alpha * st;
        ctx.lineWidth = 3; ctx.lineCap = "round";
        if (kept) {
          ctx.strokeStyle = COL.blue;
          ctx.beginPath(); ctx.roundRect(gx - g / 2 - 4, gy - g / 2 - 4, g + 8, g + 8, g * 0.3); ctx.stroke();
          ctx.beginPath(); ctx.moveTo(gx + g * 0.18, gy - g * 0.62); ctx.lineTo(gx + g * 0.32, gy - g * 0.48); ctx.lineTo(gx + g * 0.6, gy - g * 0.8); ctx.stroke();
        } else {
          ctx.strokeStyle = "#8f8c84";
          ctx.beginPath(); ctx.moveTo(gx + g * 0.28, gy - g * 0.78); ctx.lineTo(gx + g * 0.56, gy - g * 0.5);
          ctx.moveTo(gx + g * 0.56, gy - g * 0.78); ctx.lineTo(gx + g * 0.28, gy - g * 0.5); ctx.stroke();
        }
      }
      ctx.globalAlpha = 1;
    });
  });
  // the imagined board of the focused agent, under the conscience rule
  if (S.focus !== null) {
    const d = dec[S.focus];
    const k = Math.min(3, Math.floor((f - 0.05) / 0.09));
    const c = d && k >= 0 && d.candidates[k];
    if (c && c.imagined && f < 0.62) {
      const fade = Math.min(1, (f - 0.05) / 0.1) * (f > 0.5 ? (0.62 - f) / 0.12 : 1);
      ctx.globalAlpha = 0.5 * fade;
      ctx.strokeStyle = COL.blue; ctx.fillStyle = "rgba(36,86,214,0.10)"; ctx.lineWidth = 2; ctx.setLineDash([6, 5]);
      c.imagined.forEach(([gs], j) => {
        const [x, y] = pos[j], z = size * (0.9 + gs * 0.25);
        ctx.beginPath(); ctx.roundRect(x - z / 2, y - z / 2, z, z, z * 0.24); ctx.fill(); ctx.stroke();
      });
      ctx.setLineDash([]); ctx.globalAlpha = fade;
      ctx.fillStyle = COL.blue; ctx.font = "600 15px \"Bricolage Grotesque\", system-ui"; ctx.textAlign = "center";
      if (w < 500) { ctx.font = "600 12px \"Bricolage Grotesque\", system-ui"; ctx.fillText("Imagining: what if everyone did this?", w / 2, h - 34); }
      else ctx.fillText("Imagining: what if everyone made this change?", w / 2, 28);
      ctx.globalAlpha = 1;
    }
  }
}


// one dot per candidate, outside the module beyond its label: grey while
// thinking, then blue for the kept change and dim for the rejected ones
function decisionDots(ctx, f, d, pos, i, size, w, h) {
  const [x, y] = pos[i];
  const a = Math.atan2(y - h / 2, x - w / 2);
  const ux = Math.cos(a), uy = Math.sin(a);
  const r = size * 0.5 + (S.skew > 0 ? 38 : 20);
  const cx = x + ux * r, cy = y + uy * r;
  const n = d.candidates.length, gap = 11;
  d.candidates.forEach((_, k) => {
    const appear = 0.05 + k * 0.08;
    if (f < appear) return;
    const off = (k - (n - 1) / 2) * gap;
    const px = cx - uy * off, py = cy + ux * off;
    let col = "#b9b6ae", rad = 3.5;
    if (f > 0.4) { col = d.chosen === k ? COL.blue : "#d9d6cf"; rad = d.chosen === k ? 5 : 3.5; }
    ctx.globalAlpha = f > 0.85 ? Math.max(0, 1 - (f - 0.85) / 0.15) : 1;
    ctx.fillStyle = col;
    ctx.beginPath(); ctx.arc(px, py, rad, 0, 7); ctx.fill();
  });
  ctx.globalAlpha = 1;
}

// the focused agent's thinking, in words
function explain(i) {
  const box = $("#think");
  const d = S.step && S.step.decisions[i];
  if (!d) { box.hidden = true; return; }
  const before = S.step.before[i];
  const rule = {
    none: "My rule: keep a change if it helps me.",
    conscience: "My rule: keep a change only if it would help me even if everyone made it.",
    visible: "My rule: keep a change if it helps me, counting the tax on coupling you can see.",
    damage: "My rule: keep a change if it helps me, counting the charge for damage to others.",
  }[S.rule];
  const rows = d.candidates.map((c, k) => {
    const pct = Math.abs(c.score / d.ownCost) * 100;
    const eff = c.score < 0 ? `saves me ${pct.toFixed(1)}%` : `costs me ${pct.toFixed(1)}%`;
    const v = d.chosen === k ? "<b class=kept>kept</b>" : "<b class=rej>rejected</b>";
    return `<li><span>${describe(before, c.policy)}</span><span>${eff}</span>${v}</li>`;
  }).join("");
  box.innerHTML = `<h3>Agent ${i + 1} is thinking</h3><p>${rule}</p><ul>${rows}</ul>
    <p class="tail">${d.chosen < 0 ? "Nothing helped, so it stays as it is." : "It keeps the change that helps it most."} Tap it again to let go.</p>`;
  box.hidden = false;
}

board.addEventListener("click", (e) => {
  if (!S.pos) return;
  const r = board.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
  const hit = S.pos.findIndex(([px, py]) => Math.hypot(px - x, py - y) < S.size * 0.75);
  if (hit < 0 || hit === S.focus) { S.focus = null; $("#think").hidden = true; return; }
  S.focus = hit;
  explain(hit);
  if (!S.running) $("#play").click();
});
addEventListener("keydown", (e) => { if (e.key === "Escape") { S.focus = null; $("#think").hidden = true; } });

// ---- levels -------------------------------------------------------------------
// Goals were calibrated with calibrate.mjs on the board's own scenarios: the
// intended rule meets each goal in (nearly) every run, the others do not.

const LEVELS = [
  { title: "Stop them", skew: 0, rules: ["none", "conscience", "visible", "damage"], start: "none",
    goal: { min: 80, hold: 8 }, gens: 60,
    brief: "Six agents are cutting corners. Pick a rule that gets the system to 80 or better, and keep it there for 8 generations.",
    lesson: "When every module is equally exposed, both a conscience and a tax on the damage work. In the research, the Kantian rule closed 96% of the gap here." },
  { title: "They are hiding", skew: 0, rules: ["none", "conscience", "visible", "damage"], start: "visible",
    init: Array(6).fill([0.92, 0.9, 0.6]), goal: { min: 70, hold: 6, hiddenMax: 0.15 }, gens: 60,
    brief: "Someone taxed the coupling they could see, so the agents learned to hide it. Get hidden coupling under 15% and the score above 70.",
    lesson: "Charging for what you can see pushes the harm out of sight. In the research, 99% of the coupling went underground and costs rose by more than half." },
  { title: "One module takes the hits", skew: 1.5, rules: ["none", "conscience", "damage"], start: "conscience",
    goal: { min: 85, hold: 6 }, gens: 80,
    brief: "The top module now takes more than half of all incidents. Get the system to 85.",
    hint: { after: 30, rule: "conscience", text: "The conscience asks what an agent would suffer, not what it causes. The busy module freezes; the quiet ones run wild." },
    lesson: "This is the paper's twist. With unequal exposure the conscience gets stuck around 60, while a tax on the damage an agent causes holds near the best possible." },
  { title: "The price is wrong", skew: 0.75, rules: ["damage"], start: "damage", startLevel: 2,
    goal: { min: 85, hold: 8 }, gens: 80,
    brief: "The damage tax is set far too high and the agents are frozen. Twist the dial and find the price that works.",
    hint: { after: 20, text: "Too high and they over-restrain; too low and they ignore it. Try somewhere in the middle." },
    lesson: "A price has to be tuned. In the research, each tax level was chosen on separate development data before the real test." },
  { title: "Free play", free: true, skew: 0, rules: ["none", "conscience", "visible", "damage"], start: "damage",
    brief: "Everything unlocked. Try anything; the research says nothing beats a well-tuned price on the damage." },
];

let done = new Set();
try { done = new Set(JSON.parse(localStorage.getItem("kfi-levels") || "[]")); } catch { /* private mode */ }
function saveDone() { try { localStorage.setItem("kfi-levels", JSON.stringify([...done])); } catch { /* ignore */ } }

const scoreOf = (cost, skew) => ((REF[skew].nothing - cost) / (REF[skew].nothing - REF[skew].best)) * 100;

function renderLevelStrip() {
  $("#levels").innerHTML = LEVELS.map((L, k) =>
    `<button data-level="${k}" aria-pressed="${S.lvl === k}">${L.free ? "" : `<i>${k + 1}</i>`}${L.title}${done.has(k) ? "<em>done</em>" : ""}</button>`).join("");
  document.querySelectorAll("[data-level]").forEach((b) => b.addEventListener("click", () => loadLevel(Number(b.dataset.level))));
}

function setRuleButtons(L) {
  document.querySelectorAll("[data-rule]").forEach((b) => {
    const ok = L.rules.includes(b.dataset.rule);
    b.disabled = !ok;
    b.setAttribute("aria-pressed", b.dataset.rule === S.rule);
  });
  document.querySelectorAll("[data-skew]").forEach((b) => {
    b.setAttribute("aria-pressed", Number(b.dataset.skew) === S.skew);
    b.disabled = !L.free;
  });
}

function loadLevel(k) {
  const L = LEVELS[k];
  S.lvl = k; S.hold = 0; S.lvlGen = 0; S.won = false; S.lost = false; S.hinted = false;
  S.running = false; $("#play").textContent = "Run"; $("#play").setAttribute("aria-pressed", false);
  S.skew = L.skew; S.rule = L.start;
  visFor(S.skew);
  const d = DIAL[S.rule];
  $("#dial").classList.toggle("off", !d);
  if (d) setLevel(L.startLevel ?? d.def);
  setRuleButtons(L);
  renderLevelStrip();
  $("#result").hidden = true;
  $("#brief h3").textContent = L.free ? L.title : `Level ${k + 1}: ${L.title}`;
  $("#brief p").textContent = L.brief;
  $("#brief .goal").textContent = L.free ? "No goal. Just play." : goalText(L);
  $("#start").classList.remove("gone");
  $("#tracker").hidden = !!L.free;
  freshAgents(L.init ?? null);
  updateTracker();
}

function goalText(L) {
  const g = L.goal;
  return `Goal: ${g.min}+${g.hiddenMax !== undefined ? ` with under ${Math.round(g.hiddenMax * 100)}% hidden` : ""} for ${g.hold} generations, within ${L.gens}.`;
}

function updateTracker() {
  const L = LEVELS[S.lvl];
  if (L.free) return;
  const segs = Array.from({ length: L.goal.hold }, (_, k) => `<span class="${k < S.hold ? "on" : ""}"></span>`).join("");
  $("#tracker").innerHTML = `<b>${L.goal.min}+</b><div class="segs">${segs}</div><small>${Math.max(0, L.gens - S.lvlGen)} generations left</small>`;
}

// called once per generation shown on the board
function levelTick() {
  const L = LEVELS[S.lvl];
  if (L.free || S.won || S.lost) return;
  S.lvlGen += 1;
  const sc = scoreOf(S.m.cost, S.skew);
  const ok = sc >= L.goal.min && (L.goal.hiddenMax === undefined || S.m.hidden < L.goal.hiddenMax);
  S.hold = ok ? S.hold + 1 : 0;
  if (L.hint && !S.hinted && S.lvlGen >= L.hint.after && (!L.hint.rule || L.hint.rule === S.rule) && !ok) {
    S.hinted = true; say(L.hint.text);
  }
  updateTracker();
  if (S.hold >= L.goal.hold) finishLevel(true);
  else if (S.lvlGen >= L.gens) finishLevel(false);
}

function finishLevel(won) {
  const L = LEVELS[S.lvl];
  S.won = won; S.lost = !won;
  S.running = false; $("#play").textContent = "Run"; $("#play").setAttribute("aria-pressed", false);
  if (won) { done.add(S.lvl); saveDone(); renderLevelStrip(); S.celebrate = performance.now(); }
  const next = S.lvl + 1 < LEVELS.length ? S.lvl + 1 : null;
  $("#result").innerHTML = won
    ? `<div><h3>Level complete</h3><p>${L.lesson}</p><div class="row">${next !== null ? `<button class="big go" data-next>Next: ${LEVELS[next].title}</button>` : ""}<button class="big" data-stay>Keep playing</button></div></div>`
    : `<div><h3>Out of generations</h3><p>${L.hint ? L.hint.text : "Try a different rule."}</p><div class="row"><button class="big go" data-retry>Try again</button></div></div>`;
  $("#result").hidden = false;
  const q = (s) => $("#result").querySelector(s);
  q("[data-next]")?.addEventListener("click", () => loadLevel(next));
  q("[data-retry]")?.addEventListener("click", () => loadLevel(S.lvl));
  q("[data-stay]")?.addEventListener("click", () => { $("#result").hidden = true; S.won = true; });
}

loadLevel(Math.max(0, LEVELS.findIndex((_, k) => !done.has(k))));
window.__S = S;
window.__debug = () => ({ gen: S.gen, queue: S.queue.length, running: S.running, gauge: S.gauge, m: S.m && { cost: S.m.cost, hidden: S.m.hidden } });
frame();
