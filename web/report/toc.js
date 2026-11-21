// Highlights, in the contents sidebar, the section being read, and keeps that
// entry in view when the list is taller than the window.
//
// The current section is the last heading that has scrolled past the line just
// under the sticky bar. Two edge cases:
//  - at the very top, before any heading reaches that line, it is the first one;
//  - at the very bottom, short last sections can never reach the line, so the
//    last heading on screen wins, unless the reader just clicked an entry that is
//    on screen, in which case that entry stays highlighted.
(() => {
  const toc = document.querySelector("nav.toc");
  if (!toc) return;
  const links = [...toc.querySelectorAll('a[href^="#"]')];
  const heads = links.map((a) => document.getElementById(decodeURIComponent(a.hash.slice(1)))).filter(Boolean);
  if (!heads.length) return;
  const LINE = 120; // px from the top of the window: just under the sticky bar
  let clicked = null, current = null;

  function pick() {
    const atBottom = window.scrollY + window.innerHeight >= document.documentElement.scrollHeight - 2;
    if (atBottom) {
      if (clicked) {
        const r = clicked.getBoundingClientRect();
        if (r.top >= 0 && r.top < window.innerHeight) return clicked;
      }
      const onScreen = heads.filter((h) => h.getBoundingClientRect().top < window.innerHeight);
      return onScreen[onScreen.length - 1];
    }
    let cur = heads[0];
    // whole pixels, as the browser rounds when it decides what is under a point
    for (const h of heads) { if (Math.floor(h.getBoundingClientRect().top) <= LINE + 2) cur = h; else break; }
    return cur;
  }

  function update() {
    const h = pick();
    if (h === current) return;
    current = h;
    links.forEach((a) => {
      const on = a.hash.slice(1) === h.id;
      if (on) a.setAttribute("aria-current", "true"); else a.removeAttribute("aria-current");
    });
    // keep the highlighted entry inside the list's visible part
    const a = links.find((x) => x.hash.slice(1) === h.id);
    if (!a) return;
    const lr = a.getBoundingClientRect(), tr = toc.getBoundingClientRect();
    if (lr.top < tr.top + 40 || lr.bottom > tr.bottom - 8) toc.scrollTop += lr.top - tr.top - tr.height / 3;
  }

  links.forEach((a) => a.addEventListener("click", () => {
    clicked = document.getElementById(decodeURIComponent(a.hash.slice(1)));
    setTimeout(update, 0);
  }));
  // a reader scrolling by hand releases the clicked entry
  ["wheel", "touchstart", "keydown"].forEach((ev) => addEventListener(ev, () => { clicked = null; }, { passive: true }));
  addEventListener("scroll", update, { passive: true });
  addEventListener("resize", update);
  update();
})();
