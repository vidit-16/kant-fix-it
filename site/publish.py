"""Copy the live site from site/ into web/, the folder Vercel serves.

Only the files the pages load are copied: no tests, calibration tools or build
scripts. web/ is replaced entirely, so run this after any change to the site:

    python site/report/build.py   # if docs/REPORT.md changed
    python site/publish.py
"""
import shutil
from pathlib import Path

SITE = Path(__file__).resolve().parent
WEB = SITE.parent / "web"

FILES = [
    "index.html", "site.css", "site.js", "favicon.svg", "og.png",
    "game/index.html", "game/game.js", "game/worker.js", "game/game.css",
    "engine/model.js", "engine/scenarios.js", "engine/evolve.js",
    "report/index.html", "report/report.css", "report/toc.js",
]

if WEB.exists():
    shutil.rmtree(WEB)
for f in FILES:
    dst = WEB / f
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SITE / f, dst)
print(f"copied {len(FILES)} files into {WEB}")
