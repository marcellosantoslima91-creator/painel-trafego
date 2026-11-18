import base64, sys
from playwright.sync_api import sync_playwright
D = sys.argv[1]
prev = base64.b64encode(open("posts/2026-11-18-quanto-investir/slide03.jpg","rb").read()).decode()
cover = base64.b64encode(open("posts/2026-11-18-como-o-google-ve/slide01.jpg","rb").read()).decode()
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
f"""<div class=tag>Saiu hoje no feed</div><h1>Como o Google vê o seu <span class=hl>negócio?</span></h1>
<img src='data:image/jpeg;base64,{cover}' style='width:600px;margin:60px auto 0;border-radius:24px;box-shadow:0 30px 80px rgba(0,0,0,.6);transform:rotate(-3deg)'>
<p style='margin-top:70px;text-align:center'>5 pontos que decidem se o cliente <b>liga ou passa ao concorrente</b>. Toque no perfil 👆</p>""",
"""<div class=tag>Caixa de perguntas</div><h1>Qual é a maior dúvida sobre <span class=hl>anúncios?</span></h1>
<p style='margin-top:40px'>Orçamento, Instagram, Google, por onde começar… <b>Pode perguntar.</b></p>
<div style='height:440px'></div>
<p style='text-align:center;font-size:40px'>As melhores respostas vão para os Stories ☝️</p>""",
f"""<div class=tag>Spoiler 👀</div><h1>Quanto investir por mês em <span class=hl>anúncios?</span></h1>
<div style='position:relative;width:560px;margin:56px auto 0;border-radius:24px;overflow:hidden;transform:rotate(2deg);box-shadow:0 30px 80px rgba(0,0,0,.6)'><img src='data:image/jpeg;base64,{prev}' style='width:100%;display:block;filter:blur(14px)'><div style='position:absolute;inset:0;display:flex;align-items:center;justify-content:center;background:rgba(14,21,37,.35)'><span style='background:#FFB020;color:#0E1525;font-weight:800;font-size:44px;padding:20px 36px;border-radius:14px'>Amanhã, 9h, no feed</span></div></div>
<p style='margin-top:60px;text-align:center'>A conta simples que define <b>o valor certo para o negócio</b>. Ative as notificações 🔔</p>"""
]
with sync_playwright() as pw:
    b = pw.chromium.launch(executable_path="/usr/bin/google-chrome")
    pg = b.new_page(viewport={"width":1080,"height":1920})
    for i,s in enumerate(stories,1):
        pg.set_content(f"<html><head><meta charset=utf-8><style>{CSS}</style></head><body><div class=brand>@kmdmidias</div><div class=wrap>{s}</div></body></html>"); pg.wait_for_timeout(300)
        pg.screenshot(path=f"{D}/story{i:02d}.jpg", type="jpeg", quality=92)
    b.close()
