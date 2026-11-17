"""Gera slides JPEG 1080x1350 no estilo KMD.
Uso: python3 tools/gerar_slides.py post.json pasta_saida
post.json: {"slides": ["<html do slide 1>", "..."]}
Classes disponíveis: tag, h1, h2, p, b, hl (destaque amarelo), num (número grande), box (caixa com barra), cta (botão).
"""
import json, sys, os
from playwright.sync_api import sync_playwright
CSS = """
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1350px;background:#0E1525;color:#F4F1EA;font-family:'Poppins',sans-serif;position:relative;overflow:hidden}
.wrap{position:absolute;inset:110px 96px 150px 96px;display:flex;flex-direction:column;justify-content:center}
.tag{font-family:'Inter';font-weight:600;font-size:30px;letter-spacing:4px;color:#FFB020;text-transform:uppercase;margin-bottom:36px}
h1{font-weight:800;font-size:96px;line-height:1.05;letter-spacing:-2px}
h2{font-weight:700;font-size:70px;line-height:1.1;letter-spacing:-1px;margin-bottom:44px}
p{font-family:'Inter';font-size:40px;line-height:1.45;color:#C9CEDA}
p b{color:#F4F1EA}
.hl{color:#FFB020}
.num{font-weight:800;font-size:220px;line-height:.8;color:#FFB020;margin-bottom:30px}
.box{margin-top:44px;border-left:8px solid #FFB020;background:#172137;padding:30px 36px;font-family:'Inter';font-size:36px;line-height:1.4;color:#F4F1EA}
.foot{position:absolute;left:96px;right:96px;bottom:70px;display:flex;justify-content:space-between;font-family:'Inter';font-size:28px;color:#7D869A}
.foot b{color:#F4F1EA;font-weight:600}
.bar{position:absolute;top:0;left:0;height:14px;background:#FFB020}
.cta{display:inline-block;margin-top:50px;background:#FFB020;color:#0E1525;font-weight:800;font-size:44px;padding:26px 44px;border-radius:14px}
"""
def main(src, out):
    slides = json.load(open(src))["slides"]
    os.makedirs(out, exist_ok=True)
    chrome = "/usr/bin/google-chrome" if os.path.exists("/usr/bin/google-chrome") else None
    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=chrome) if chrome else pw.chromium.launch()
        pg = b.new_page(viewport={"width":1080,"height":1350})
        n = len(slides)
        for i, s in enumerate(slides, 1):
            nav = f"{i}/{n}" + (" — desliza →" if i < n else "") if n > 1 else "@kmdmidias"
            html = f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body><div class=bar style='width:{(i/n)*1080}px'></div><div class=wrap>{s}</div><div class=foot><b>KMD Mídias Digitais</b><span>{nav}</span></div></body></html>"
            pg.set_content(html); pg.wait_for_timeout(200)
            pg.screenshot(path=os.path.join(out, f"slide{i:02d}.jpg"), type="jpeg", quality=92)
        b.close()
if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
