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

function face(ctx, x, y, s, mood, blink) {
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
      else { ctx.beginPath(); ctx.arc(x + k * ex, ey, e, 0, 7); ctx.fill(); }
    }
    ctx.beginPath(); ctx.moveTo(x - s * .11, y + s * .19); ctx.lineTo(x + s * .11, y + s * .19); ctx.stroke();
  }
}

function module(ctx, x, y, s, mood, heat, blink, ring = null) {
  ctx.fillStyle = "#fff"; ctx.beginPath(); ctx.roundRect(x - s / 2, y - s / 2, s, s, s * .24); ctx.fill();
  if (heat > 0) { ctx.globalAlpha = heat; ctx.fillStyle = C.red; ctx.beginPath(); ctx.roundRect(x - s / 2, y - s / 2, s, s, s * .24); ctx.fill(); ctx.globalAlpha = 1; }
  ctx.strokeStyle = ring || "#cfccc4"; ctx.lineWidth = ring ? 4 : 2;
  ctx.beginPath(); ctx.roundRect(x - s / 2, y - s / 2, s, s, s * .24); ctx.stroke();
  face(ctx, x, y, s, mood, blink);
}

// ---- hero: six agents on a ring, sharing wires; incidents land at random ----
const hero = document.querySelector("#heroBoard");
const H = { hits: [0, 0, 0, 0, 0, 0], smug: [0, 0, 0, 0, 0, 0], sparks: [], next: 0 };
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
    module(ctx, x + (Math.random() - .5) * sh, y + bob, s, mood, hot ? .5 * (1 - since / 700) : 0, ((t / 1000 + i * .8) % 4) < .12);
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

// ---- findings charts: published numbers, bars from zero ------------------------
function hbars(el, rows, { max, fmt, note }) {
  const W = Math.max(300, Math.min(640, el.clientWidth - 8)), small = W < 460;
  const rowH = small ? 40 : 46, labelW = small ? 118 : 190, H = rows.length * rowH + 6, fs = small ? 13 : 16, vs = small ? 13 : 15;
  const room = small ? 56 : 150;
  const x = (v) => labelW + (Math.max(0, v) / max) * (W - labelW - room);
  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${el.dataset.title}">${rows.map((r, k) => {
    const y = k * rowH + 4;
    return `<text x="0" y="${y + 24}" font-size="${fs}" font-weight="600" fill="${C.ink}">${small ? r.short || r.label : r.label}</text>
      <rect x="${labelW}" y="${y + 6}" width="${W - labelW - room}" height="26" rx="8" fill="${C.bg}"/>
      <rect class="grow" x="${labelW}" y="${y + 6}" width="${Math.max(2, x(r.value) - labelW)}" height="26" rx="8" fill="${r.color}"/>
      <text x="${x(r.value) + 8}" y="${y + 25}" font-size="${vs}" font-weight="700" fill="${C.ink}">${fmt(r.value)}${r.tag && !small ? ` ${r.tag}` : ""}</text>`;
  }).join("")}</svg>${note ? `<p class="note">${note}</p>` : ""}`;
}

const pct = (v) => `${Math.round(v * 100)}%`;
function drawCharts() {
hbars(document.querySelector("#chartPay"), [
  { label: "Selfish agents", value: 1.125, color: C.grey },
  { label: "A conscience", value: 0.997, color: C.ink },
  { label: "Welfare of a joint move", short: "Joint welfare", value: 0.864, color: C.ink },
  { label: "A price on delay", value: 0.815, color: C.blue },
], { max: 1.2, fmt: (v) => v.toFixed(3), note: "System cost per unit of payments, held-out scenarios, 20 seeds. Lower is better." });

hbars(document.querySelector("#chartHide"), [
  { label: "Selfish agents", value: 0.2384, color: C.grey },
  { label: "A conscience", value: 0.2147, color: C.ink },
  { label: "Tax the damage", value: 0.2156, color: C.blue },
  { label: "Tax visible coupling", short: "Visible tax", value: 0.3665, color: C.red, tag: "· 98% hidden" },
], { max: 0.4, fmt: (v) => v.toFixed(3), note: "System cost per unit of output, shared codebase, 20 seeds. Lower is better." });

// share of the selfish-to-best gap each rule closes (E10)
function groups(el, sets, labels) {
  const W = Math.max(300, Math.min(640, el.clientWidth - 8)), small = W < 460;
  const H = 250, gw = (W - 20) / sets.length, bw = small ? 30 : 46, base = 210, top = 24, fs = small ? 13 : 15;
  const y = (v) => base - (Math.max(0, Math.min(1.05, v)) * (base - top));
  el.innerHTML = `<svg viewBox="0 0 ${W} ${H}" role="img" aria-label="${el.dataset.title}">
    <rect x="0" y="${y(1)}" width="${W}" height="2" fill="${C.bg}"/>
    ${sets.map((g, k) => {
      const gx = 10 + k * gw + gw / 2;
      return `${g.bars.map((b, j) => {
        const bx = gx + (j - g.bars.length / 2) * (bw + 8) + 4;
        return `<rect class="growy" x="${bx}" y="${y(b.v)}" width="${bw}" height="${base - y(b.v)}" rx="8" fill="${b.c}"/>
          <text x="${bx + bw / 2}" y="${y(b.v) - 8}" font-size="${fs}" font-weight="700" text-anchor="middle" fill="${C.ink}">${pct(b.v)}</text>`;
      }).join("")}<text x="${gx}" y="${base + 26}" font-size="${fs}" font-weight="600" text-anchor="middle" fill="${C.ink}">${small ? g.short : g.label}</text>`;
    }).join("")}</svg><p class="note">${labels}</p>`;
}
groups(document.querySelector("#chartUnequal"), [
  { label: "All equally exposed", short: "Equal", bars: [{ v: 0.96, c: C.ink }, { v: 0.92, c: C.blue }] },
  { label: "Some take more", short: "Some more", bars: [{ v: 0.92, c: C.ink }, { v: 0.99, c: C.blue }] },
  { label: "One takes most", short: "One most", bars: [{ v: 0.67, c: C.ink }, { v: 1.0, c: C.blue }] },
], "Share of the damage fixed, where 100% is the best possible. Black: the conscience. Blue: the damage tax. 20 seeds per bar.");

hbars(document.querySelector("#chartUnits"), [
  { label: "Conscience, linear", short: "Linear", value: 0.67, color: C.ink },
  { label: "Conscience, logit", short: "Logit", value: 0.92, color: C.ink },
  { label: "Conscience, square root", short: "Square root", value: 0.54, color: C.ink },
  { label: "Conscience, log", short: "Log", value: 0, color: C.red, tag: "(worse than nothing)" },
  { label: "Tax the damage", short: "Damage tax", value: 1.0, color: C.blue },
], { max: 1.05, fmt: pct, note: "Share of the damage fixed when one module takes most incidents, for four ways of measuring “the same change”. 20 seeds each." });

}
drawCharts();
let chartTimer = null;
addEventListener("resize", () => { clearTimeout(chartTimer); chartTimer = setTimeout(drawCharts, 150); });

// ---- entrances ------------------------------------------------------------------
const els = document.querySelectorAll(".rise");
if (REDUCED || !("IntersectionObserver" in window)) els.forEach((e) => e.classList.add("in"));
else {
  const io = new IntersectionObserver((es) => es.forEach((en) => { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } }), { rootMargin: "0px 0px -8% 0px" });
  els.forEach((e) => io.observe(e));
}
