"""Gera frames 1080x1920 (Reel) no estilo KMD e monta o MP4 com ffmpeg.
Uso: python3 tools/gerar_reel.py <reel.json> <pasta_saida> [segundos_por_frame]
Zona segura: texto entre 260px do topo e 420px do fundo (interface do Instagram)."""
import json, os, sys, subprocess
from playwright.sync_api import sync_playwright
sys.path.insert(0, os.path.dirname(__file__))
from gerar_slides import CSS
REEL_CSS = CSS.replace("height:1350px", "height:1920px") + \
  ".wrap{inset:260px 96px 420px 96px}.foot{bottom:330px}h1{font-size:104px}"
def main(src, out, secs=3.6):
    frames = json.load(open(src))["frames"]
    os.makedirs(out, exist_ok=True)
    chrome = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=chrome) if chrome else pw.chromium.launch()
        pg = b.new_page(viewport={"width":1080,"height":1920})
        n = len(frames)
        for i, s in enumerate(frames, 1):
            html = f"<html><head><meta charset=utf-8><style>{REEL_CSS}</style></head><body><div class=bar style='width:{(i/n)*1080}px'></div><div class=wrap>{s}</div><div class=foot><b>KMD Mídias Digitais</b><span>@kmdmidias</span></div></body></html>"
            pg.set_content(html); pg.wait_for_timeout(200)
            pg.screenshot(path=os.path.join(out, f"frame{i:02d}.jpg"), type="jpeg", quality=92)
        b.close()
    secs = float(secs); fade = 0.4
    inputs = []
    for i in range(1, n + 1):
        inputs += ["-loop", "1", "-t", str(secs), "-i", os.path.join(out, f"frame{i:02d}.jpg")]
    chain, last = [], "[0:v]"
    for i in range(1, n):
        off = round(i * (secs - fade), 3)
        chain.append(f"{last}[{i}:v]xfade=transition=fade:duration={fade}:offset={off}[v{i}]")
        last = f"[v{i}]"
    flt = ";".join(chain) + f";{last}format=yuv420p[vout]" if chain else "[0:v]format=yuv420p[vout]"
    subprocess.run(["ffmpeg", "-y", *inputs, "-f", "lavfi", "-t", str(n*(secs-fade)+fade), "-i", "anullsrc=r=44100:cl=stereo",
                    "-filter_complex", flt, "-map", "[vout]", "-map", f"{n}:a", "-c:v", "libx264", "-preset", "veryfast",
                    "-r", "30", "-c:a", "aac", "-shortest", "-movflags", "+faststart", os.path.join(out, "reel.mp4")],
                   check=True, capture_output=True)
if __name__ == "__main__":
    main(*sys.argv[1:])
