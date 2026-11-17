import base64, sys
from playwright.sync_api import sync_playwright
D = sys.argv[1]
cover = base64.b64encode(open("posts/2026-11-18-meta-vs-google/slide01.jpg","rb").read()).decode()
CSS = """*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;background:#0E1525;color:#F4F1EA;font-family:'Poppins';position:relative;overflow:hidden}
.wrap{position:absolute;inset:260px 90px 360px 90px;display:flex;flex-direction:column;justify-content:center}
.tag{font-family:'Inter';font-weight:600;font-size:34px;letter-spacing:5px;color:#FFB020;text-transform:uppercase;margin-bottom:34px}
h1{font-weight:800;font-size:100px;line-height:1.05;letter-spacing:-2px}
p{font-family:'Inter';font-size:44px;line-height:1.45;color:#C9CEDA}
b{color:#F4F1EA}.hl{color:#FFB020}
.box{margin-top:50px;border-left:10px solid #FFB020;background:#172137;padding:36px 40px;font-family:'Inter';font-size:42px;line-height:1.4}
.brand{position:absolute;left:90px;top:150px;font-family:'Inter';font-weight:600;font-size:32px;color:#7D869A}
"""
stories = [
f"""<div class=tag>Acabou de sair 🔥</div><h1>Post novo no <span class=hl>feed</span></h1>
<img src='data:image/jpeg;base64,{cover}' style='width:620px;margin:60px auto 0;border-radius:24px;box-shadow:0 30px 80px rgba(0,0,0,.6);transform:rotate(-3deg)'>
<p style='margin-top:70px;text-align:center'>Meta Ads ou Google Ads? <b>Toque no perfil</b> e veja qual faz sentido para o seu negócio 👆</p>""",
"""<div class=tag>Mito ou verdade?</div><h1>“Se o anúncio não vende, é só pôr <span class=hl>mais dinheiro</span>.”</h1>
<p style='margin-top:90px;font-size:40px;color:#7D869A'>Resposta 👇</p>
<div class=box><b class=hl style='font-size:56px;font-family:Poppins'>MITO.</b><br>Se a oferta ou o público estão errados, mais orçamento só <b>acelera o prejuízo</b>. Primeiro corrige-se a base — depois escala-se.</div>""",
"""<div class=tag>Pergunta rápida</div><h1>Já investiu em anúncios para o seu <span class=hl>negócio?</span></h1>
<div style='height:420px'></div>
<p style='text-align:center;font-size:40px'>Responda aqui em cima ☝️<br>Quem disser “ainda não” recebe uma dica personalizada.</p>"""
]
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width":1080,"height":1920})
    for i,s in enumerate(stories,1):
        pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body><div class=brand>@kmdmidias</div><div class=wrap>{s}</div></body></html>"); pg.wait_for_timeout(300)
        pg.screenshot(path=f"{D}/story{i:02d}.jpg", type="jpeg", quality=92)
    b.close()
