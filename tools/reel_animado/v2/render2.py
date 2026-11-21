"""Uso: python3 render2.py reels/x.html pasta_saida [KEYS="t1 t2" só para frames-chave]
O HTML define window.D, window.S, window.STYLE, window.SFX e setTime(t); opcional showCover()."""
import os, sys, json, subprocess, shutil
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
src, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); os.makedirs(out, exist_ok=True)
FPS=30; tmpd=f"{out}/.tmp"; os.makedirs(tmpd, exist_ok=True)
keys=os.environ.get("KEYS")
with sync_playwright() as pw:
    b=pw.chromium.launch(); pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("file://"+src); pg.wait_for_timeout(500)
    D=pg.evaluate("window.D"); S=pg.evaluate("window.S"); STYLE=pg.evaluate("window.STYLE"); SFX=pg.evaluate("window.SFX")
    if keys:
        for t in map(float,keys.split()): pg.evaluate(f"setTime({t})"); pg.screenshot(path=f"{tmpd}/key_{t}.jpg",type="jpeg",quality=80)
        if pg.evaluate("typeof showCover==='function'"): pg.evaluate("showCover()"); pg.screenshot(path=f"{tmpd}/key_capa.jpg",type="jpeg",quality=80)
        b.close(); sys.exit(0)
    for i,(a,e) in enumerate(S,1):
        tmp=f"{tmpd}/scene{i}.tmp.mp4"
        p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate",str(FPS),"-c:v","mjpeg","-i","-",
            "-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),"-f","mp4",tmp],stdin=subprocess.PIPE)
        for f in range(round(a*FPS),round(e*FPS)):
            pg.evaluate(f"setTime({f/FPS})"); p.stdin.write(pg.screenshot(type="jpeg",quality=92))
        p.stdin.close(); assert p.wait()==0
        os.rename(tmp,f"{tmpd}/scene{i}.mp4")
    if pg.evaluate("typeof showCover==='function'"):
        pg.evaluate("showCover()"); pg.wait_for_timeout(100); pg.screenshot(path=f"{out}/capa.jpg",type="jpeg",quality=92)
    b.close()
open(f"{tmpd}/list.txt","w").write("".join(f"file 'scene{i}.mp4'\n" for i in range(1,len(S)+1)))
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",f"{tmpd}/list.txt","-c","copy",f"{tmpd}/video.mp4"],check=True)
json.dump({"style":STYLE,"D":D,"sfx":SFX},open(f"{tmpd}/som.json","w"))
subprocess.run([sys.executable,f"{HERE}/som_estilos.py",f"{tmpd}/som.json",f"{tmpd}/som.wav"],check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{tmpd}/video.mp4","-i",f"{tmpd}/som.wav","-map","0:v","-map","1:a","-c:v","copy",
  "-af","loudnorm=I=-14:TP=-1.5:LRA=9","-c:a","aac","-b:a","192k","-ar","44100","-shortest","-movflags","+faststart",f"{out}/reel.tmp.mp4"],check=True)
os.rename(f"{out}/reel.tmp.mp4",f"{out}/reel.mp4"); shutil.copy(src,f"{out}/reel_animado.html"); shutil.rmtree(tmpd)
print("ok",out)
