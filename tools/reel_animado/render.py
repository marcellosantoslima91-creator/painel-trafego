import os, subprocess
from playwright.sync_api import sync_playwright
FPS=30; S=[(0,3.6),(3.6,7.6),(7.6,11.6),(11.6,15.6),(15.6,20.0)]
chrome="/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
with sync_playwright() as pw:
    b=pw.chromium.launch(executable_path=chrome) if chrome else pw.chromium.launch()
    pg=b.new_page(viewport={"width":1080,"height":1920})
    pg.goto("file://"+os.path.abspath("reel.html")); pg.wait_for_timeout(400)
    for i,(a,e) in enumerate(S,1):
        f0,f1=round(a*FPS),round(e*FPS)
        tmp=f"scene{i}.tmp.mp4"
        p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","image2pipe","-framerate",str(FPS),"-c:v","mjpeg","-i","-",
            "-c:v","libx264","-crf","18","-preset","veryfast","-pix_fmt","yuv420p","-r",str(FPS),"-f","mp4",tmp],stdin=subprocess.PIPE)
        for f in range(f0,f1):
            pg.evaluate(f"setTime({f/FPS})")
            p.stdin.write(pg.screenshot(type="jpeg",quality=92))
        p.stdin.close(); assert p.wait()==0
        os.rename(tmp,f"scene{i}.mp4")
    b.close()
open("list.txt","w").write("".join(f"file 'scene{i}.mp4'\n" for i in range(1,6)))
subprocess.run(["ffmpeg","-y","-loglevel","error","-f","concat","-safe","0","-i","list.txt","-c","copy","video.mp4"],check=True)
subprocess.run(["ffmpeg","-y","-loglevel","error","-i","video.mp4","-f","lavfi","-i","anullsrc=r=44100:cl=stereo","-map","0:v","-map","1:a","-c:v","copy","-c:a","aac","-shortest","-movflags","+faststart","reel.mp4"],check=True)
