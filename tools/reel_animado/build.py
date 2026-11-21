"""Gera um Reel animado KMD (20 s, com som) + capa a partir de um cfg.json.
Uso: python3 build.py cfg.json pasta_saida"""
import json, os, sys, subprocess, shutil
from playwright.sync_api import sync_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
cfg_path, out = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]); os.makedirs(out, exist_ok=True)
cfg=json.load(open(cfg_path)); js=json.dumps(cfg, ensure_ascii=False)
html=open(f"{HERE}/reel_template.html").read().replace("/*CFG*/{}", js)
open(f"{out}/reel_animado.html","w").write(html)
capa=open(f"{HERE}/capa_modelo.html").read().replace("/*CFG*/{}", js)
open(f"{out}/capa.html","w").write(capa)
FPS=30; S=[(0,3.6),(3.6,7.2),(7.2,11.6),(11.6,15.6),(15.6,20.0)]
tmpd=f"{out}/.tmp"; os.makedirs(tmpd, exist_ok=True)
keys=[float(x) for x in os.environ.get("KEYS","").split()] if os.environ.get("KEYS") else None
with sync_playwright() as pw:
    b=pw.chromium.launch(); pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("file://"+f"{out}/capa.html"); pg.wait_for_timeout(300); pg.screenshot(path=f"{out}/capa.jpg",type="jpeg",quality=92)
    pg.goto("file://"+f"{out}/reel_animado.html"); pg.wait_for_timeout(400)
    if keys:
        for t in keys: pg.evaluate(f"setTime({t})"); pg.screenshot(path=f"{tmpd}/key_{t}.jpg",type="jpeg",quality=80)
        b.close(); sys.exit(0)
    for i,(a,e) in enumerate(S,1):
        tmp=f"{tmpd}/scene{i}.tmp.mp4"
        p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate",str(FPS),"-c:v","mjpeg","-i","-",
            "-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),"-f","mp4",tmp],stdin=subprocess.PIPE)
        for f in range(round(a*FPS),round(e*FPS)):
            pg.evaluate(f"setTime({f/FPS})"); p.stdin.write(pg.screenshot(type="jpeg",quality=92))
        p.stdin.close(); assert p.wait()==0
        os.rename(tmp,f"{tmpd}/scene{i}.mp4")
    b.close()
open(f"{tmpd}/list.txt","w").write("".join(f"file 'scene{i}.mp4'\n" for i in range(1,6)))
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i",f"{tmpd}/list.txt","-c","copy",f"{tmpd}/video.mp4"],check=True)
env=dict(os.environ, REEL_CFG=cfg_path, REEL_WAV=f"{tmpd}/som.wav")
subprocess.run([sys.executable, f"{HERE}/som_modelo.py"], check=True, env=env, cwd=tmpd, stdout=subprocess.DEVNULL)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i",f"{tmpd}/video.mp4","-i",f"{tmpd}/som.wav","-map","0:v","-map","1:a","-c:v","copy",
  "-af","loudnorm=I=-14:TP=-1.5:LRA=9","-c:a","aac","-b:a","192k","-ar","44100","-shortest","-movflags","+faststart",f"{out}/reel.mp4.tmp.mp4"],check=True)
os.rename(f"{out}/reel.mp4.tmp.mp4", f"{out}/reel.mp4"); shutil.rmtree(tmpd)
print("ok", out)
