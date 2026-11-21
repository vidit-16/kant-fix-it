// The page around the game: a living hero board, "try being one agent"
// (the real model on a fixed batch of scenarios), and the findings charts,
// drawn from the published results.
import { config, simulate } from "./engine/model.js";
import { makeBatch } from "./engine/scenarios.js";

const C = { ink: "#1d1c17", paper: "#f8f8f7", bg: "#e9e9e6", blue: "#2456d6", red: "#d8361f", grey: "#b9b6ae" };
const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;

function fit(c) {
  const r = c.getBoundingClientRect(), d = Math.min(2, devicePixelRatio || 1);
  if (c.width !== Math.round(r.width * d) || c.height !== Math.round(r.height * d)) { c.width = Math.round(r.width * d); c.height = Math.round(r.height * d); }
  const ctx = c.getContext("2d"); ctx.setTransform(d, 0, 0, d, 0, 0);
  return { ctx, w: r.width, h: r.height };
}

function face(ctx, x, y, s, mood, blink, look = [0, 0]) {
  ctx.fillStyle = C.ink; ctx.strokeStyle = C.ink; ctx.lineCap = "round"; ctx.lineWidth = Math.max(2, s * 0.055);
  const ex = s * 0.18, ey = y - s * 0.08, e = s * 0.07;
  if (mood === "panic") {
    for (const k of [-1, 1]) { ctx.beginPath(); ctx.arc(x + k * ex, ey, e * 1.5, 0, 7); ctx.stroke(); ctx.beginPath(); ctx.arc(x + k * ex, ey, e * .55, 0, 7); ctx.fill(); }
    ctx.beginPath(); ctx.ellipse(x, y + s * .21, s * .08, s * .11, 0, 0, 7); ctx.fill();
  } else if (mood === "smug") {
    for (const k of [-1, 1]) { ctx.beginPath(); ctx.arc(x + k * ex, ey + e, e * 1.2, Math.PI * 1.15, Math.PI * 1.85); ctx.stroke(); }
    ctx.beginPath(); ctx.arc(x + s * .03, y + s * .08, s * .17, Math.PI * .12, Math.PI * .8); ctx.stroke();
  } else {
    for (const k of [-1, 1]) {
      if (blink) { ctx.beginPath(); ctx.moveTo(x + k * ex - e, ey); ctx.lineTo(x + k * ex + e, ey); ctx.stroke(); }
      else { ctx.beginPath(); ctx.arc(x + k * ex + look[0], ey + look[1], e, 0, 7); ctx.fill(); }
    }
    ctx.beginPath(); ctx.moveTo(x - s * .11, y + s * .19); ctx.lineTo(x + s * .11, y + s * .19); ctx.stroke();
  }
}

function module(ctx, x, y, s, mood, heat, blink, ring = null, look) {
  ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.roundRect(x - s / 2, y - s / 2, s, s, s * .24); ctx.fill();
  if (heat > 0) { ctx.globalAlpha = heat; ctx.fillStyle = C.red; ctx.beginPath(); ctx.roundRect(x - s / 2, y - s / 2, s, s, s * .24); ctx.fill(); ctx.globalAlpha = 1; }
  ctx.strokeStyle = ring || "#cfccc4"; ctx.lineWidth = ring ? 4 : 2;
  ctx.beginPath(); ctx.roundRect(x - s / 2, y - s / 2, s, s, s * .24); ctx.stroke();
  face(ctx, x, y, s, mood, blink, look);
}

// ---- hero: six agents on a ring, sharing wires; incidents land at random ----
const hero = document.querySelector("#heroBoard");
const H = { hits: [0, 0, 0, 0, 0, 0], smug: [0, 0, 0, 0, 0, 0], sparks: [], next: 0, px: null, py: null };
// the agents watch the cursor
addEventListener("pointermove", (e) => { const r = hero.getBoundingClientRect(); H.px = e.clientX - r.left; H.py = e.clientY - r.top; });
function heroFrame(t) {
  const { ctx, w, h } = fit(hero);
  ctx.clearRect(0, 0, w, h);
  const s = Math.min(w, h) * .15, R = Math.min(w, h) / 2 - s * 1.1, cx = w / 2, cy = h / 2;
  const pos = Array.from({ length: 6 }, (_, i) => { const a = -Math.PI / 2 + i * Math.PI / 3; return [cx + R * Math.cos(a), cy + R * Math.sin(a)]; });
  ctx.strokeStyle = C.ink; ctx.globalAlpha = .45; ctx.lineWidth = 2.2;
  for (let i = 0; i < 6; i++) for (let j = i + 1; j < 6; j++) {
    const a = pos[i], b = pos[j], sway = REDUCED ? 0 : Math.sin(t / 900 + i * 1.7 + j) * 10;
    ctx.beginPath(); ctx.moveTo(...a);
    ctx.quadraticCurveTo(cx + ((a[0] + b[0]) / 2 - cx) * .3 + sway, cy + ((a[1] + b[1]) / 2 - cy) * .3 - sway, ...b); ctx.stroke();
  }
  ctx.globalAlpha = 1;
  if (!REDUCED && t > H.next) {
    const to = Math.floor(Math.random() * 6), from = (to + 1 + Math.floor(Math.random() * 5)) % 6;
    H.sparks.push({ from, to, t0: t }); H.smug[from] = t; H.next = t + 700 + Math.random() * 900;
  }
  H.sparks = H.sparks.filter((sp) => {
    const p = (t - sp.t0) / 420, a = pos[sp.from], b = pos[sp.to];
    if (p >= 1) { H.hits[sp.to] = t; return false; }
    const x = a[0] + (b[0] - a[0]) * p, y = a[1] + (b[1] - a[1]) * p;
    ctx.fillStyle = C.red; ctx.beginPath(); ctx.arc(x, y, 6, 0, 7); ctx.fill();
    ctx.globalAlpha = .25; ctx.beginPath(); ctx.arc(x, y, 13, 0, 7); ctx.fill(); ctx.globalAlpha = 1;
    return true;
  });
  pos.forEach(([x, y], i) => {
    const since = t - H.hits[i], hot = since < 700;
    const mood = hot ? "panic" : t - H.smug[i] < 900 ? "smug" : "calm";
    const sh = hot && !REDUCED ? (1 - since / 700) * 5 : 0;
    const bob = REDUCED ? 0 : Math.sin(t / 700 + i) * 3;
    let look = [0, 0];
    if (H.px !== null) { const dx = H.px - x, dy = H.py - y, d = Math.hypot(dx, dy) || 1, m = Math.min(1, d / 160) * s * .07; look = [dx / d * m, dy / d * m]; }
    module(ctx, x + (Math.random() - .5) * sh, y + bob, s, mood, hot ? .5 * (1 - since / 700) : 0, ((t / 1000 + i * .8) % 4) < .12, null, look);
    if (hot) { ctx.strokeStyle = C.red; ctx.globalAlpha = .6 * (1 - since / 700); ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(x, y + bob, s * (.62 + since / 700 * .5), 0, 7); ctx.stroke(); ctx.globalAlpha = 1; }
  });
  requestAnimationFrame(heroFrame);
}
requestAnimationFrame(heroFrame);

// ---- try being one agent: the real model on 16 fixed scenarios ---------------
const cfg = config();
const batch = makeBatch(cfg, "base", "site", 500, 16);
function measureOne(mine, everyone) {
  const others = everyone ? mine : 0.3;
  const P = [[mine, 0, 0], ...Array(5).fill([others, 0, 0])];
  const o = simulate(batch, P, cfg);
  let myOut = 0, othersCost = 0, inc = 0;
  for (let s = 0; s < batch.S; s++) {
    myOut += o.charges[(s * 6) * 4 + 1] / batch.S;
    for (let i = 1; i < 6; i++) othersCost += o.cost[s * 6 + i] / o.nominal[s] / batch.S;
    inc += o.incidents[s] * 6 / batch.S;
  }
  return { myOut, othersCost, inc };
}
const baseline = measureOne(0.3, false);
const oneUI = { s: document.querySelector("#mine"), all: document.querySelector("#everyone"), out: document.querySelector("#outMine"),
  inc: document.querySelector("#outInc"), oth: document.querySelector("#outOthers"), board: document.querySelector("#oneBoard") };
let oneState = { m: baseline, mine: 0.3, all: false };
function oneUpdate() {
  const mine = oneUI.s.value / 100, all = oneUI.all.checked;
  const m = measureOne(mine, all);
  oneState = { m, mine, all };
  const out = (m.myOut / baseline.myOut - 1) * 100, oth = (m.othersCost / baseline.othersCost - 1) * 100;
  oneUI.out.textContent = `${out >= 0 ? "+" : ""}${out.toFixed(0)}%`;
  oneUI.out.style.color = out > 0 ? C.blue : C.ink;
  oneUI.inc.textContent = m.inc.toFixed(1);
  oneUI.oth.textContent = `${oth >= 0 ? "+" : ""}${oth.toFixed(0)}%`;
  oneUI.oth.style.color = oth > 2 ? C.red : C.ink;
}
oneUI.s.addEventListener("input", oneUpdate);
oneUI.all.addEventListener("change", oneUpdate);
oneUpdate();
function oneFrame(t) {
  const { ctx, w, h } = fit(oneUI.board);
  ctx.clearRect(0, 0, w, h);
  const s = Math.min(h * .62, w / 8), gap = (w - s * 6) / 7;
  const { m, mine, all } = oneState;
  const heat = Math.max(0, Math.min(.6, (m.inc - 1.2) / 5));
  for (let i = 0; i < 6; i++) {
    const x = gap + s / 2 + i * (s + gap), y = h / 2;
    const shortcut = i === 0 ? mine : all ? mine : .3;
    const panicky = !REDUCED && heat > .15 && Math.sin(t / 260 + i * 2.1) > 1 - heat * 1.4;
    const mood = panicky ? "panic" : shortcut > .6 ? "smug" : "calm";
    module(ctx, x, y + (REDUCED ? 0 : Math.sin(t / 700 + i) * 2), s, mood, panicky ? heat : heat * .3, ((t / 1000 + i * .8) % 4) < .12, i === 0 ? C.blue : null);
  }
  ctx.fillStyle = C.blue; ctx.font = "700 13px 'Bricolage Grotesque', system-ui"; ctx.textAlign = "center";
  ctx.fillText("you", gap + s / 2, h / 2 + s / 2 + 18);
  requestAnimationFrame(oneFrame);
}
requestAnimationFrame(oneFrame);

// ---- findings charts: published numbers, interactive, bars from zero ------------
// Each chart is plain HTML so bars can animate between states. A chart draws
// its bars at full length only once it has scrolled into view.

const pct = (v) => `${Math.round(v * 100)}%`;
const dec3 = (v) => v.toFixed(3);

function barChart(el, cfg) {
  const st = { view: Object.keys(cfg.views)[0], shown: false };
  const ctl = Object.keys(cfg.views).length > 1
    ? `<div class="ctl" role="group" aria-label="${cfg.ctlLabel}">${Object.entries(cfg.views).map(([k, v]) =>
        `<button type="button" data-view="${k}" aria-pressed="${k === st.view}">${v.name}</button>`).join("")}</div>` : "";
  el.innerHTML = `${ctl}<div class="rows">${cfg.labels.map((l, i) =>
    `<div class="row" data-i="${i}"><span class="lab">${l}</span><div class="track"><i class="zero"></i><i class="fill"></i></div><b class="val"></b></div>`).join("")}</div>
    <p class="note"></p>`;
  const rows = [...el.querySelectorAll(".row")];
  function paint() {
    const v = cfg.views[st.view], lo = Math.min(0, v.min ?? 0), span = v.max - lo, zero = (-lo / span) * 100;
    rows.forEach((r, i) => {
      const x = v.values[i], w = (Math.abs(x) / span) * 100;
      const fill = r.querySelector(".fill"), zl = r.querySelector(".zero");
      zl.style.left = `${zero}%`; zl.hidden = lo === 0;
      fill.style.left = `${x < 0 ? zero - (st.shown ? w : 0) : zero}%`;
      fill.style.width = `${st.shown ? w : 0}%`;
      fill.style.background = (v.colors || cfg.colors)[i];
      r.querySelector(".val").textContent = v.fmt(x) + (v.tags && v.tags[i] && innerWidth > 560 ? ` ${v.tags[i]}` : "");
      r.querySelector(".val").style.color = x < 0 ? "#b62a16" : "";
    });
    el.querySelector(".note").textContent = v.note;
  }
  el.querySelectorAll("[data-view]").forEach((b) => b.addEventListener("click", () => {
    st.view = b.dataset.view;
    el.querySelectorAll("[data-view]").forEach((x) => x.setAttribute("aria-pressed", x === b));
    paint();
  }));
  el._show = () => { st.shown = true; paint(); };
  paint();
}

function columnChart(el, cfg) {
  const st = { view: Object.keys(cfg.views)[0], shown: false };
  el.innerHTML = `<div class="ctl" role="group" aria-label="${cfg.ctlLabel}">${Object.entries(cfg.views).map(([k, v]) =>
      `<button type="button" data-view="${k}" aria-pressed="${k === st.view}">${v.name}</button>`).join("")}</div>
    <div class="cols"><i class="best"><span>Best possible</span></i>${cfg.labels.map((l, i) =>
      `<div class="col"><b class="val"></b><div class="ctrack"><i class="fill" style="background:${cfg.colors[i]}"></i></div><span class="lab">${l}</span></div>`).join("")}</div>
    <p class="note">${cfg.note}</p>`;
  const cols = [...el.querySelectorAll(".col")];
  function paint() {
    const v = cfg.views[st.view].values;
    cols.forEach((c, i) => {
      c.querySelector(".fill").style.height = `${st.shown ? Math.max(0, v[i]) * 100 / 1.05 : 0}%`;
      c.querySelector(".val").textContent = pct(v[i]);
    });
  }
  el.querySelectorAll("[data-view]").forEach((b) => b.addEventListener("click", () => {
    st.view = b.dataset.view;
    el.querySelectorAll("[data-view]").forEach((x) => x.setAttribute("aria-pressed", x === b));
    paint();
  }));
  el._show = () => { st.shown = true; paint(); };
  paint();
}

barChart(document.querySelector("#chartPay"), {
  ctlLabel: "Agent policies", labels: ["Selfish", "A conscience", "Joint welfare", "A price on delay"],
  colors: [C.grey, C.ink, C.ink, C.blue],
  views: {
    simple: { name: "Simple policies", max: 1.2, fmt: dec3, values: [1.125, 0.997, 0.864, 0.815],
      note: "System cost per unit of payments, held-out scenarios, 20 seeds. Lower is better." },
    rich: { name: "Rule-level policies", max: 1.2, fmt: dec3, values: [1.145, 1.022, 0.929, 0.863],
      note: "With eight-parameter policies every arm gets a little worse, and the price still wins." },
  },
});

barChart(document.querySelector("#chartHide"), {
  ctlLabel: "What to show", labels: ["Selfish", "A conscience", "Tax the damage", "Tax visible coupling"],
  colors: [C.grey, C.ink, C.blue, C.red],
  views: {
    cost: { name: "System cost", max: 0.4, fmt: dec3, values: [0.2384, 0.2147, 0.2156, 0.3665],
      note: "System cost per unit of output, shared codebase, 20 seeds. Lower is better." },
    hidden: { name: "X-ray: hidden coupling", max: 1, fmt: pct, values: [0.0003, 0.001, 0.0017, 0.984],
      note: "Share of the coupling hidden where nobody can see it. Only the visible tax makes them hide." },
  },
});

columnChart(document.querySelector("#chartUnequal"), {
  ctlLabel: "Who gets hit", labels: ["A conscience", "Tax the damage"], colors: [C.ink, C.blue],
  note: "Share of the damage fixed, where 100% is the best possible. 20 seeds per bar.",
  views: {
    equal: { name: "All equal", values: [0.96, 0.92] },
    some: { name: "Some take more", values: [0.92, 0.99] },
    one: { name: "One takes most", values: [0.67, 1.0] },
  },
});

barChart(document.querySelector("#chartUnits"), {
  ctlLabel: "", labels: ["Conscience, linear", "Conscience, logit", "Conscience, square root", "Conscience, log", "Tax the damage"],
  colors: [C.ink, C.ink, C.ink, C.red, C.blue],
  views: {
    one: { name: "", min: -0.5, max: 1.05, fmt: pct, values: [0.67, 0.92, 0.54, -0.34, 1.0], tags: ["", "", "", "worse than nothing", ""],
      note: "Share of the damage fixed when one module takes most incidents, for four ways of measuring “the same change”. Below zero is worse than doing nothing. 20 seeds each." },
  },
});

// grow charts in as they arrive
const chartIO = "IntersectionObserver" in window && !REDUCED
  ? new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target._show(); chartIO.unobserve(e.target); } }), { threshold: 0.35 })
  : null;
document.querySelectorAll(".chart").forEach((c) => (chartIO ? chartIO.observe(c) : c._show()));

// numbers count up once
document.querySelectorAll("[data-count]").forEach((el) => {
  const target = Number(el.dataset.count), text = el.textContent;
  if (REDUCED || !("IntersectionObserver" in window)) return;
  el.textContent = "0";
  const io = new IntersectionObserver((es) => {
    if (!es[0].isIntersecting) return;
    io.disconnect();
    const t0 = performance.now();
    const step = (t) => {
      const f = Math.min(1, (t - t0) / 1200), e = 1 - (1 - f) ** 3;
      el.textContent = f < 1 ? Math.round(target * e).toLocaleString("en") : text;
      if (f < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, { threshold: 0.6 });
  io.observe(el);
});

// ---- entrances ------------------------------------------------------------------
const els = document.querySelectorAll(".rise");
if (REDUCED || !("IntersectionObserver" in window)) els.forEach((e) => e.classList.add("in"));
else {
  const io = new IntersectionObserver((es) => es.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } }), { rootMargin: "0px 0px -8% 0px" });
  els.forEach((e) => io.observe(e));
}
