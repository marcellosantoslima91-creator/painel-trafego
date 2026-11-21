"""Motor de som: música por estilo + efeitos (SFX) em tempos dados.
uso: python3 som_estilos.py spec.json out.wav   spec={"style":..,"D":20,"sfx":[[t,"tipo",gain,param],...]}"""
import json, sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter
SR=44100
rng=np.random.default_rng(7)
def T(d): return np.arange(int(SR*d))/SR
def lp(x,fc,o=2): b,a=butter(o,min(fc,SR/2-100)/(SR/2)); return lfilter(b,a,x)
def tvlp(x,fc):
    a=1-np.exp(-2*np.pi*np.asarray(fc)/SR); y=np.zeros_like(x); z=0.0
    a=np.broadcast_to(a,x.shape)
    for i in range(len(x)): z+=a[i]*(x[i]-z); y[i]=z
    return y
def hp(x,fc,o=2): b,a=butter(o,fc/(SR/2),'high'); return lfilter(b,a,x)
def bp(x,lo,hi): b,a=butter(2,[lo/(SR/2),hi/(SR/2)],'band'); return lfilter(b,a,x)
def mtof(m): return 440*2**((m-69)/12)
def env(n,a=.005,r=.2,sus=None):
    t=np.arange(n)/SR; e=np.minimum(1,t/max(a,1e-4))
    return e*np.exp(-t/max(r,1e-3)) if sus is None else e*np.where(t<sus,1,np.exp(-(t-sus)/max(r,1e-3)))
def saw(f,t): return 2*((f*t)%1)-1
def sqr(f,t): return np.sign(np.sin(2*np.pi*f*t))
def tri(f,t): return 2*np.abs(saw(f,t))-1
# ---------- instrumentos ----------
def kick(punch=1.0,dec=.25):
    t=T(.45); f=45+120*np.exp(-t*35)*punch; ph=2*np.pi*np.cumsum(f)/SR
    return np.sin(ph)*np.exp(-t/dec)
def k808(f0=45,d=.9):
    t=T(d); f=f0+60*np.exp(-t*25); ph=2*np.pi*np.cumsum(f)/SR
    return np.tanh(2.2*np.sin(ph))*np.exp(-t/(d*.5))
def snare(tone=190,dec=.12):
    t=T(.3); n=hp(rng.standard_normal(len(t)),1500)*np.exp(-t/dec); s=np.sin(2*np.pi*tone*t)*np.exp(-t*30)
    return .7*n+.5*s
def clap():
    t=T(.35); n=bp(rng.standard_normal(len(t)),900,3500); e=np.zeros(len(t))
    for o in (0,.012,.024): e+=np.exp(-np.maximum(0,t-o)*60)*(t>=o)
    e+=np.exp(-np.maximum(0,t-.03)*12)*(t>=.03)*.6
    return n*e*.6
def hat(dec=.035,o=False):
    t=T(.4 if o else .1); return hp(rng.standard_normal(len(t)),7000)*np.exp(-t/(dec*(6 if o else 1)))*.5
def rim():
    t=T(.08); return (np.sin(2*np.pi*1700*t)+.5*hp(rng.standard_normal(len(t)),3000))*np.exp(-t*70)*.5
def shaker():
    t=T(.09); return hp(rng.standard_normal(len(t)),5000)*np.sin(np.pi*t/.09)*.35
def pad(ms,d):
    t=T(d); x=sum(saw(mtof(m)*k,t) for m in ms for k in (1,1.004,.996))/ (3*len(ms))
    return lp(x,1400)*env(len(t),.25,.6,sus=d-.3)
def stab(ms,d=.22):
    t=T(d); x=sum(saw(mtof(m),t)+sqr(mtof(m)*1.003,t)*.5 for m in ms)/len(ms)
    return lp(x,2600)*env(len(t),.003,.09)
def rhodes(ms,d):
    t=T(d); x=0
    for m in ms:
        f=mtof(m); x=x+np.sin(2*np.pi*f*t+1.2*np.sin(2*np.pi*f*t)*np.exp(-t*4))
    return x/len(ms)*env(len(t),.005,.9)*(1+.15*np.sin(2*np.pi*4.5*t))
def piano(ms,d):
    t=T(d); x=0
    for m in ms:
        f=mtof(m); x=x+sum(np.sin(2*np.pi*f*h*t)*np.exp(-t*(1.2+h*.8))/h for h in (1,2,3,4))
    return x/len(ms)*env(len(t),.003,1.2)
def pluck(m,d=.3):
    t=T(d); f=mtof(m); return lp(saw(f,t)+.5*sqr(f*2,t),3500)*env(len(t),.002,.12)
def bell(m,d=.6):
    t=T(d); f=mtof(m); return (np.sin(2*np.pi*f*t+2*np.sin(2*np.pi*f*3.5*t)*np.exp(-t*6)))*env(len(t),.002,.35)
def bassnote(m,d,kind='sine'):
    t=T(d); f=mtof(m)
    if kind=='sine': x=np.sin(2*np.pi*f*t)+.25*np.sin(4*np.pi*f*t)
    elif kind=='saw': x=tvlp(saw(f,t),500+900*np.exp(-t*12))
    elif kind=='slap': x=tvlp(sqr(f,t)*.6+np.sin(2*np.pi*f*t),1200*np.exp(-t*6)+200)
    return x*env(len(t),.004,d*.6 if kind!='sine' else d*.8,sus=d*.6)
def brass(ms,d=.25):
    t=T(d); x=sum(lp(saw(mtof(m),t)*(1+.003*np.sin(30*t)),1800) for m in ms)/len(ms)
    return x*env(len(t),.02,.12)
# ---------- estilos ----------
S={
 "pulse": dict(bpm=122, chords=[[57,60,64],[53,57,60],[55,59,62],[52,55,59]], roots=[45,41,43,40],
   kick=[0,4,8,12], clap=[4,12], hat=[2,6,10,14], ohat=[], shaker=False, bass=('saw',[0,3,6,8,11,14]), keys=('pluck_arp',None), pad=.12, swing=0),
 "ambient": dict(bpm=92, chords=[[62,66,69,73],[59,62,66,69],[55,59,62,66],[57,61,64,69]], roots=[50,47,43,45],
   kick=[0,10], clap=[], rim=[4,12], hat=[], shaker=True, bass=('sine',[0,10]), keys=('bell_arp',None), pad=.28, swing=0),
 "funk": dict(bpm=108, chords=[[64,67,71,74],[62,65,69,72],[60,64,67,71],[62,65,69,72]], roots=[40,38,36,38],
   kick=[0,3,8,10], clap=[4,12], hat=[0,2,4,6,8,10,12,14], ohat=[7,15], shaker=False, bass=('slap',[0,3,6,8,10,13]), keys=('brass',[4,11]), pad=.0, swing=.08),
 "lofi": dict(bpm=82, chords=[[62,65,69,72],[60,64,67,71],[57,60,64,67],[59,62,65,69]], roots=[50,48,45,47],
   kick=[0,7,10], clap=[], snare=[4,12], hat=[0,2,4,6,8,10,12,14], ohat=[], shaker=False, bass=('sine',[0,7,10]), keys=('rhodes',[0,8]), pad=.0, swing=.18, crackle=True, lpf=4200),
 "house": dict(bpm=124, chords=[[60,63,67,70],[58,62,65,68],[56,60,63,67],[58,62,65,68]], roots=[48,46,44,46],
   kick=[0,4,8,12], clap=[4,12], hat=[2,6,10,14], ohat=[2,6,10,14], shaker=True, bass=('saw',[2,6,10,14]), keys=('stab',[3,6,11,14]), pad=.08, swing=0),
 "piano": dict(bpm=76, chords=[[60,64,67,72],[55,59,62,67],[57,60,64,69],[53,57,60,65]], roots=[48,43,45,41],
   kick=[0,8], clap=[], rim=[12], hat=[], shaker=False, bass=('sine',[0]), keys=('piano',[0,6,10]), pad=.15, swing=0),
 "trap": dict(bpm=140, chords=[[61,64,68],[61,64,68],[57,61,64],[59,63,66]], roots=[37,37,33,35],
   kick=[0,11], clap=[8], hat=[0,2,4,6,8,10,12,14], roll=True, ohat=[], shaker=False, bass=('808',[0,11]), keys=('bell_arp',None), pad=.12, swing=0),
}
def add(buf,t0,sig,g=1.0,pan=0.0):
    i=int(t0*SR)
    if i>=len(buf) or i<0: return
    n=min(len(sig),len(buf)-i); l=g*np.sqrt((1-pan)/2); r=g*np.sqrt((1+pan)/2)
    buf[i:i+n,0]+=sig[:n]*l; buf[i:i+n,1]+=sig[:n]*r
def music(st,D,intro=.6):
    c=S[st]; spb=60/c['bpm']; s16=spb/4; bar=spb*4; buf=np.zeros((int(SR*(D+1)),2))
    nb=int(D/bar)+2
    for b in range(nb):
        t0=b*bar; ch=c['chords'][b%4]; rt=c['roots'][b%4]
        if c['pad']: add(buf,t0,pad(ch,bar+.3),c['pad'])
        for s in range(16):
            ts=t0+s*s16+(c['swing']*s16 if s%2 else 0)
            if ts<intro and st not in('ambient','piano'): continue
            if s in c['kick']: add(buf,ts,k808() if st=='trap' and False else kick(1.2 if st in('house','pulse') else 1,.18 if st=='lofi' else .25),.9)
            if s in c.get('clap',[]): add(buf,ts,clap(),.55)
            if s in c.get('snare',[]): add(buf,ts,lp(snare(170,.15),5000),.6)
            if s in c.get('rim',[]): add(buf,ts,rim(),.35,.2)
            if s in c.get('hat',[]):
                g=.22 if st!='lofi' else .14
                add(buf,ts,hat(),g,.3)
                if c.get('roll') and b%2==1 and s>=12: add(buf,ts+s16/3,hat(),g*.8,.3); add(buf,ts+2*s16/3,hat(),g*.6,.3)
            if s in c.get('ohat',[]): add(buf,ts,hat(o=True),.15,-.3)
            if c['shaker'] and st!='house': add(buf,ts,shaker(),.12,-.2)
            if c['shaker'] and st=='house' and s%2==1: add(buf,ts,shaker(),.1,-.2)
            kind,steps=c['bass']
            if s in steps:
                if kind=='808': add(buf,ts,k808(mtof(rt+12)/1 if False else mtof(rt),1.2 if s==0 else .6),.55)
                else: add(buf,ts,bassnote(rt+(12 if kind!='sine' else 12) if kind=='slap' else rt+12, s16*(3 if kind!='sine' else 6),kind),.32 if kind!='sine' else .38)
            kk,ksteps=c['keys']
            if kk=='pluck_arp' and s%2==0: add(buf,ts,pluck(ch[(s//2)%len(ch)]+12),.1,(-.4 if s%4 else .4))
            if kk=='bell_arp' and s%3==0: add(buf,ts,bell(ch[(s//3)%len(ch)]+12,.8),.08,(-.5 if s%6 else .5))
            if ksteps and s in ksteps:
                if kk=='brass': add(buf,ts,brass([m+12 for m in ch[:3]]),.18)
                if kk=='stab': add(buf,ts,stab(ch,.2),.16)
                if kk=='rhodes': add(buf,ts,rhodes(ch,bar/2+.2),.22)
                if kk=='piano': add(buf,ts,piano(ch if s==0 else [ch[-1]+12],1.6),.22)
    if c.get('crackle'):
        n=len(buf); cr=np.zeros(n); idx=rng.integers(0,n,int(D*40)); cr[idx]=rng.uniform(-.6,.6,len(idx)); cr=hp(cr,2000)
        buf[:,0]+=cr*.25; buf[:,1]+=cr*.25; buf[:,0]+=lp(rng.standard_normal(n),900)*.006; buf[:,1]+=lp(rng.standard_normal(n),900)*.006
    if c.get('lpf'): buf[:,0]=lp(buf[:,0],c['lpf']); buf[:,1]=lp(buf[:,1],c['lpf'])
    return buf[:int(SR*D)]
# ---------- SFX ----------
def whoosh(d=.45,up=True):
    t=T(d); n=rng.standard_normal(len(t)); f=np.linspace(400,4000,len(t)) if up else np.linspace(4000,400,len(t))
    out=np.zeros(len(t)); blk=512
    for i in range(0,len(t),blk): out[i:i+blk]=bp(n[i:i+blk],f[i]*.6,min(f[i]*1.4,20000))
    return out*np.sin(np.pi*t/d)*.8
def fx(kind,par=None):
    if kind=='whoosh': return whoosh(par or .45)
    if kind=='whooshdown': return whoosh(par or .6,False)
    if kind=='pop': t=T(.12); f=(par or 520)*np.exp(-t*8); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t*30)
    if kind=='thud': return kick(1.4,.2)*1.2
    if kind=='impact': t=T(1.2); return np.tanh(2*(kick(1.5,.35)[:len(t)] if False else np.pad(kick(1.5,.35),(0,len(t)-len(kick(1.5,.35))))))+lp(rng.standard_normal(len(t)),300)*np.exp(-t*3)*.8
    if kind=='ding': t=T(.6); f=par or 1318.5; return (np.sin(2*np.pi*f*t)+.4*np.sin(2*np.pi*f*2.01*t))*np.exp(-t*7)
    if kind=='buzz': t=T(.28); return np.tanh(3*sqr(110,t)*.5+saw(116,t)*.3)*np.exp(-t*6)*.6
    if kind=='click': t=T(.03); return hp(rng.standard_normal(len(t)),2500)*np.exp(-t*250)
    if kind=='tick': t=T(.05); return np.sin(2*np.pi*(par or 2400)*t)*np.exp(-t*120)
    if kind=='notif': t=T(.5); a=np.sin(2*np.pi*1046.5*t)*np.exp(-t*12); b=np.sin(2*np.pi*1568*t)*np.exp(-np.maximum(0,t-.11)*10)*(t>.11); return a+b
    if kind=='riser':
        d=par or 1.5; t=T(d); f=200*2**(t/d*3); return (lp(rng.standard_normal(len(t)),3000)*.4+np.sin(2*np.pi*np.cumsum(f)/SR)*.3)*(t/d)**2
    if kind=='shutter': t=T(.18); n=hp(rng.standard_normal(len(t)),2000); return n*(np.exp(-t*80)+np.exp(-np.maximum(0,t-.07)*80)*(t>.07))*.8
    if kind=='cash':
        t=T(.9); return (np.sin(2*np.pi*2093*t)+np.sin(2*np.pi*2637*t)*.7)*np.exp(-t*5)*.6+hp(rng.standard_normal(len(t)),4000)*np.exp(-t*40)*.4
    if kind=='glitch':
        t=T(par or .25); x=sqr(rng.choice([180,240,320,90]),t)*(rng.random(len(t))>.5); return lp(x,4000)*.4
    if kind=='swipe': return whoosh(.25)*1.2
    if kind=='bass_drop': t=T(1.0); f=120*np.exp(-t*3)+30; return np.tanh(2*np.sin(2*np.pi*np.cumsum(f)/SR))*np.exp(-t*2.5)
    if kind=='heartbeat': return np.concatenate([kick(.6,.12)[:int(.25*SR)],kick(.5,.12)])*.8
    if kind=='key': t=T(.04); return (hp(rng.standard_normal(len(t)),1800)*.6+np.sin(2*np.pi*rng.uniform(800,1200)*t)*.4)*np.exp(-t*160)
    raise ValueError(kind)
def build(spec,out):
    D=spec['D']; m=music(spec['style'],D)
    sf=np.zeros_like(m)
    for e in spec['sfx']:
        t,k=e[0],e[1]; g=e[2] if len(e)>2 else .4; par=e[3] if len(e)>3 else None
        add(sf,t,fx(k,par),g,(rng.uniform(-.25,.25)))
    # ducking ligeiro da música nos SFX fortes
    mix=m*.85+sf
    fo=int(SR*1.2); mix[-fo:]*=np.linspace(1,0,fo)[:,None]
    mix/=np.max(np.abs(mix))*1.1
    wavfile.write(out,SR,(mix*32767).astype(np.int16))
if __name__=='__main__':
    build(json.load(open(sys.argv[1])),sys.argv[2])
