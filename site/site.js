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
  const per = Array(6).fill(0);
  for (let s = 0; s < batch.S; s++) {
    myOut += o.charges[(s * 6) * 4 + 1] / batch.S;
    for (let i = 0; i < 6; i++) per[i] += o.cost[s * 6 + i] / o.nominal[s] / batch.S;
    inc += o.incidents[s] * 6 / batch.S;
  }
  for (let i = 1; i < 6; i++) othersCost += per[i];
  return { myOut, othersCost, inc, per };
}
const baseline = measureOne(0.3, false);
const oneUI = { s: document.querySelector("#mine"), all: document.querySelector("#everyone"), out: document.querySelector("#outMine"),
  inc: document.querySelector("#outInc"), oth: document.querySelector("#outOthers"), othLab: document.querySelector("#outOthersLab"),
  say: document.querySelector("#oneSay"), board: document.querySelector("#oneBoard") };
let oneState = { m: baseline, mine: 0.3, all: false, sel: null, pos: [], s: 0, sparks: [], next: 0 };
const signed = (v) => `${v >= 0 ? "+" : ""}${v.toFixed(0)}%`;
function oneUpdate() {
  const mine = oneUI.s.value / 100, all = oneUI.all.checked;
  const m = measureOne(mine, all);
  Object.assign(oneState, { m, mine, all });
  const sel = oneState.sel;
  const out = (m.myOut / baseline.myOut - 1) * 100;
  const oth = sel === null ? (m.othersCost / baseline.othersCost - 1) * 100 : (m.per[sel] / baseline.per[sel] - 1) * 100;
  oneUI.out.textContent = signed(out);
  oneUI.out.style.color = out > 0 ? C.blue : C.ink;
  oneUI.inc.textContent = m.inc.toFixed(1);
  oneUI.oth.textContent = signed(oth);
  oneUI.oth.style.color = oth > 2 ? C.red : C.ink;
  oneUI.othLab.textContent = sel === null ? "cost to the others" : `cost to agent ${sel + 1}`;
  if (sel === null) { oneUI.say.textContent = "Tap another agent to see what your shortcuts cost it."; return; }
  const n = `Agent ${sel + 1}`, p = Math.abs(oth).toFixed(0);
  oneUI.say.textContent = Math.abs(oth) < 1 ? `${n} pays about what it pays when you play fair.`
    : oth < 0 ? `You cut fewer corners than the rest, so ${n.toLowerCase()} pays ${p}% less.`
    : all ? `${n} cuts corners too now. It pays ${p}% more, and part of that comes from you.`
    : `${n} did nothing different. Your shortcuts cost it ${p}% more.`;
}
oneUI.s.addEventListener("input", oneUpdate);
oneUI.all.addEventListener("change", oneUpdate);
oneUpdate();
function agentAt(e) {
  const r = oneUI.board.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top, s = oneState.s;
  return oneState.pos.findIndex(([px, py]) => Math.abs(x - px) < s * .6 && Math.abs(y - py) < s * .6);
}
oneUI.board.addEventListener("click", (e) => {
  const i = agentAt(e);
  if (i < 0) return;
  oneState.sel = i === 0 || i === oneState.sel ? null : i;
  oneState.sparks = []; oneState.next = 0;
  oneUpdate();
});
oneUI.board.addEventListener("pointermove", (e) => { oneUI.board.style.cursor = agentAt(e) > 0 ? "pointer" : ""; });
function oneFrame(t) {
  const { ctx, w, h } = fit(oneUI.board);
  ctx.clearRect(0, 0, w, h);
  const s = Math.min(h * .55, w / 8), gap = (w - s * 6) / 7;
  const { m, mine, all, sel } = oneState;
  const heat = Math.max(0, Math.min(.6, (m.inc - 1.2) / 5));
  const y0 = h / 2 - 8;
  oneState.s = s;
  oneState.pos = Array.from({ length: 6 }, (_, i) => [gap + s / 2 + i * (s + gap), y0]);
  // sparks run from you to the agent you picked, faster the more corners you cut
  if (sel !== null && !REDUCED && mine > .05 && t > oneState.next) {
    oneState.sparks.push({ t0: t }); oneState.next = t + 1500 - 1200 * mine;
  }
  const hitAt = oneState.sparks.reduce((a, sp) => (t - sp.t0 > 520 ? Math.max(a, sp.t0 + 520) : a), -1e9);
  oneState.sparks = oneState.sparks.filter((sp) => t - sp.t0 < 1300);
  for (let i = 0; i < 6; i++) {
    const [x, y] = oneState.pos[i];
    const shortcut = i === 0 ? mine : all ? mine : .3;
    const struck = i === sel && t - hitAt < 600;
    const panicky = struck || (!REDUCED && heat > .15 && Math.sin(t / 260 + i * 2.1) > 1 - heat * 1.4);
    const mood = panicky ? "panic" : shortcut > .6 ? "smug" : "calm";
    const ring = i === 0 ? C.blue : i === sel ? C.red : null;
    module(ctx, x, y + (REDUCED ? 0 : Math.sin(t / 700 + i) * 2), s, mood, struck ? .45 * (1 - (t - hitAt) / 600) : panicky ? heat : heat * .3, ((t / 1000 + i * .8) % 4) < .12, ring);
  }
  if (sel !== null) {
    const a = oneState.pos[0], b = oneState.pos[sel];
    for (const sp of oneState.sparks) {
      const p = (t - sp.t0) / 520;
      if (p > 1) continue;
      const x = a[0] + (b[0] - a[0]) * p, y = a[1] - Math.sin(p * Math.PI) * s * .9;
      ctx.fillStyle = C.red; ctx.beginPath(); ctx.arc(x, y, 5, 0, 7); ctx.fill();
      ctx.globalAlpha = .25; ctx.beginPath(); ctx.arc(x, y, 11, 0, 7); ctx.fill(); ctx.globalAlpha = 1;
    }
  }
  ctx.font = "700 13px 'Bricolage Grotesque', system-ui"; ctx.textAlign = "center";
  ctx.fillStyle = C.blue; ctx.fillText("you", oneState.pos[0][0], y0 + s / 2 + 18);
  if (sel !== null) { ctx.fillStyle = "#b62a16"; ctx.fillText(`agent ${sel + 1}`, oneState.pos[sel][0], y0 + s / 2 + 18); }
  requestAnimationFrame(oneFrame);
}
requestAnimationFrame(oneFrame);

// ---- findings charts: published numbers, interactive, bars from zero ------------
// Each chart is plain HTML so bars can animate between states. A chart draws
// its bars at full length only once it has scrolled into view.

const pct = (v) => `${Math.round(v * 100)}%`;
const dec3 = (v) => v.toFixed(3);

// the view switch, with a nudge until someone uses it
function ctlHTML(cfg, view) {
  if (Object.keys(cfg.views).length < 2) return "";
  return `<div class="ctlbar"><div class="ctl" role="group" aria-label="${cfg.ctlLabel}">${Object.entries(cfg.views).map(([k, v]) =>
    `<button type="button" data-view="${k}" aria-pressed="${k === view}">${v.name}</button>`).join("")}</div><button type="button" class="cmp-next">Tap to compare</button></div>`;
}
function wireCtl(el, st, paint) {
  const views = [...el.querySelectorAll("[data-view]")];
  views.forEach((b) => b.addEventListener("click", () => {
    st.view = b.dataset.view;
    views.forEach((x) => x.setAttribute("aria-pressed", x === b));
    el.querySelector(".ctlbar")?.classList.add("used");
    paint();
  }));
  // the hint is a button too: it moves to the next view
  el.querySelector(".cmp-next")?.addEventListener("click", () => {
    const k = views.findIndex((b) => b.dataset.view === st.view);
    views[(k + 1) % views.length].click();
  });
}
// hover (mouse) previews a bar's meaning; a tap or Enter pins it
// Every explanation sits in the same grid cell and only one is visible, so the
// box is always as tall as the longest one: nothing moves when it changes.
function explainer(el, items, labels, why) {
  const box = el.querySelector(".why");
  box.innerHTML = `<span data-k="-1">Tap a bar to see what it means.</span>` +
    why.map((w, k) => `<span data-k="${k}"><b>${labels[k]}.</b> ${w}</span>`).join("");
  const spans = [...box.children];
  let pinned = null;
  const show = (i) => {
    items.forEach((r, k) => { r.classList.toggle("dim", i !== null && k !== i); r.setAttribute("aria-pressed", k === i); });
    box.classList.toggle("on", i !== null);
    spans.forEach((s) => s.classList.toggle("cur", Number(s.dataset.k) === (i ?? -1)));
  };
  items.forEach((r, i) => {
    r.tabIndex = 0; r.setAttribute("role", "button");
    r.addEventListener("pointerenter", (e) => { if (e.pointerType === "mouse") show(i); });
    r.addEventListener("pointerleave", (e) => { if (e.pointerType === "mouse") show(pinned); });
    r.addEventListener("click", () => { pinned = pinned === i ? null : i; show(pinned); });
    r.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); r.click(); } });
  });
  show(null);
}

function barChart(el, cfg) {
  const st = { view: Object.keys(cfg.views)[0], shown: false };
  el.innerHTML = `${ctlHTML(cfg, st.view)}<div class="rows">${cfg.labels.map((l, i) =>
    `<div class="row" data-i="${i}"><span class="lab">${l}</span><div class="track"><i class="zero"></i><i class="fill"></i></div><b class="val"></b></div>`).join("")}</div>
    <p class="why" aria-live="polite"></p><p class="note"></p>`;
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
  wireCtl(el, st, paint);
  explainer(el, rows, cfg.labels, cfg.why);
  el._show = () => { st.shown = true; paint(); };
  paint();
}

function columnChart(el, cfg) {
  const st = { view: Object.keys(cfg.views)[0], shown: false };
  el.innerHTML = `${ctlHTML(cfg, st.view)}
    <div class="cols"><i class="best"><span>Best possible</span></i>${cfg.labels.map((l, i) =>
      `<div class="col"><b class="val"></b><div class="ctrack"><i class="fill" style="background:${cfg.colors[i]}"></i></div><span class="lab">${l}</span></div>`).join("")}</div>
    <p class="why" aria-live="polite"></p><p class="note">${cfg.note}</p>`;
  const cols = [...el.querySelectorAll(".col")];
  function paint() {
    const v = cfg.views[st.view].values;
    cols.forEach((c, i) => {
      c.querySelector(".fill").style.height = `${st.shown ? Math.max(0, v[i]) * 100 / 1.05 : 0}%`;
      c.querySelector(".val").textContent = pct(v[i]);
    });
  }
  wireCtl(el, st, paint);
  explainer(el, cols, cfg.labels, cfg.why);
  el._show = () => { st.shown = true; paint(); };
  paint();
}

barChart(document.querySelector("#chartPay"), {
  ctlLabel: "Agent policies", labels: ["Selfish", "A conscience", "Joint welfare", "A price on delay"],
  colors: [C.grey, C.ink, C.ink, C.blue],
  why: [
    "No rule. Each bank holds back payments to save its own cash, everyone ends up waiting, and the network costs the most.",
    "Before keeping a change, each bank asks “what if every bank did this?”. Clearly better than selfish, but well short of the price.",
    "Each bank counts every other bank’s costs as if they were its own. Close to the price, still behind it.",
    "A plain charge for every period a payment waits, tuned on separate development data. The cheapest network of all.",
  ],
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
  why: [
    "No rule. Agents add coupling whenever it helps them ship, and the incidents land on everyone.",
    "Agents ask “what if everyone made this change?” before keeping it. Cuts the damage, and hides nothing.",
    "Agents pay for the incidents they cause, wherever those land. There is nothing to gain by hiding.",
    "Agents pay for the coupling anyone can see. They learned to hide it instead: 98% went out of sight and costs rose by more than half.",
  ],
  views: {
    cost: { name: "System cost", max: 0.4, fmt: dec3, values: [0.2384, 0.2147, 0.2156, 0.3665],
      note: "System cost per unit of output, shared codebase, 20 seeds. Lower is better." },
    hidden: { name: "X-ray: hidden coupling", max: 1, fmt: pct, values: [0.0003, 0.001, 0.0017, 0.984],
      note: "Share of the coupling hidden where nobody can see it. Only the visible tax makes them hide." },
  },
});

columnChart(document.querySelector("#chartUnequal"), {
  ctlLabel: "Who gets hit", labels: ["A conscience", "Tax the damage"], colors: [C.ink, C.blue],
  why: [
    "“What if everyone did this?” measures what an agent would suffer, not what it causes. As exposure gets unequal, the exposed agent freezes and the sheltered ones run wild.",
    "Each agent pays for the damage it causes. It holds near the best possible however unevenly the incidents fall.",
  ],
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
  why: [
    "The original rule: “the same change” means the same amount added for everyone.",
    "The same change measured on a logit scale. The best of the four, still short of the tax.",
    "The same change measured on a square-root scale. Worse than the original.",
    "The same change measured in proportion, on a log scale. Here the conscience leaves the system worse than having no rule at all.",
    "The damage tax, for comparison. No scale to choose: an agent pays for what it causes.",
  ],
  views: {
    one: { name: "", min: -0.5, max: 1.05, fmt: pct, values: [0.67, 0.92, 0.54, -0.34, 1.0], tags: ["", "", "", "worse than nothing", ""],
      note: "Share of the damage fixed when one module takes most incidents, for four ways of measuring “the same change”. Below zero is worse than doing nothing. 20 seeds each." },
  },
});

// grow charts in as they arrive
const chartIO = "IntersectionObserver" in window && !REDUCED
  ? new IntersectionObserver((es) => es.forEach((e) => { if (e.isIntersecting) { e.target._show(); e.target.classList.add("live"); chartIO.unobserve(e.target); } }), { threshold: 0.35 })
  : null;
document.querySelectorAll(".chart").forEach((c) => (chartIO ? chartIO.observe(c) : c._show()));

// "try it in the game": load that level, then scroll to the board
document.querySelectorAll("[data-goto]").forEach((a) => a.addEventListener("click", (e) => {
  if (!window.kfiGame) return;
  e.preventDefault();
  window.kfiGame.loadLevel(Number(a.dataset.goto));
  document.querySelector("#game").scrollIntoView({ behavior: REDUCED ? "auto" : "smooth" });
  history.replaceState(null, "", "#game");
}));

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
