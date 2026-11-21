"""Faixa original para o Reel do café: batida lo-fi + efeitos sincronizados com a animação."""
import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter

SR = 44100
DUR = 20.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))

def t_arr(d): return np.arange(int(SR * d)) / SR
def env(n, a=0.005, r=0.2):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    nr = min(n, int(r * SR)); e[-nr:] *= np.linspace(1, 0, nr) ** 2; return e
def lp(x, fc):
    b, a = butter(2, fc / (SR / 2), 'low'); return lfilter(b, a, x)
def hp(x, fc):
    b, a = butter(2, fc / (SR / 2), 'high'); return lfilter(b, a, x)
def add(buf, start, sig, gain=1.0, pan=0.0):
    i = int(start * SR); j = min(len(buf), i + len(sig))
    if i >= len(buf) or j <= i: return
    s = sig[: j - i] * gain
    buf[i:j, 0] += s * (1 - pan) ; buf[i:j, 1] += s * (1 + pan)
def note(f): return 440.0 * 2 ** ((f - 69) / 12)

# ---------- música ----------
BPM = 104; B = 60 / BPM
def kick():
    t = t_arr(0.35); f = 120 * np.exp(-t * 18) + 45
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
def snare():
    t = t_arr(0.22); n = hp(rng.standard_normal(len(t)), 1500) * np.exp(-t * 22)
    return 0.6 * n + 0.3 * np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
def hat():
    t = t_arr(0.06); return hp(rng.standard_normal(len(t)), 7000) * np.exp(-t * 70)
def pad(freqs, d):
    t = t_arr(d); s = np.zeros(len(t))
    for f in freqs:
        for det in (-0.12, 0.12):
            s += np.sin(2 * np.pi * (f + det) * t) + 0.25 * np.sin(4 * np.pi * (f + det) * t)
    return lp(s / (len(freqs) * 2), 2200) * env(len(t), 0.25, 0.4)
def keys(f, d):
    t = t_arr(d); s = np.sin(2 * np.pi * f * t) * np.exp(-t * 3) + 0.3 * np.sin(4 * np.pi * f * t) * np.exp(-t * 5)
    return s * env(len(t), 0.003, 0.1)
def bass(f, d):
    t = t_arr(d); s = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)
    return lp(s, 400) * env(len(t), 0.01, 0.08)

chords = [[60, 64, 67, 71], [57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65]]  # Cmaj7 Am7 Fmaj7 G7
roots = [48, 45, 41, 43]
bar = 4 * B
nbars = int(DUR / bar) + 1
for bi in range(nbars):
    t0 = bi * bar; c = chords[bi % 4]; r = roots[bi % 4]
    add(music, t0, pad([note(m) for m in c], bar + 0.3), 0.22)
    add(music, t0, bass(note(r), B * 1.5), 0.16); add(music, t0 + B * 2.5, bass(note(r), B * 1.2), 0.13)
    arp = [c[0], c[2], c[1], c[3], c[2], c[0] + 12, c[3], c[1]]
    for k, m in enumerate(arp):
        add(music, t0 + k * B / 2, keys(note(m + 12), B), 0.11, pan=0.3 if k % 2 else -0.3)
    for beat in range(4):
        tb = t0 + beat * B
        if tb < 0.9: continue  # intro mais limpa
        if beat in (0, 2): add(music, tb, kick(), 0.55)
        if beat in (1, 3): add(music, tb, snare(), 0.22)
        add(music, tb, hat(), 0.08, pan=0.4); add(music, tb + B / 2, hat(), 0.05, pan=0.4)
# fade out final
fo = int(1.2 * SR); music[-fo:] *= np.linspace(1, 0, fo)[:, None]

# ---------- efeitos ----------
def whoosh(d=0.45, up=True):
    t = t_arr(d); n = rng.standard_normal(len(t)); sw = np.linspace(0, 1, len(t))
    out = np.zeros(len(t)); seg = 512
    for i in range(0, len(t), seg):
        fc = 300 + 5000 * (sw[i] if up else 1 - sw[i]); out[i:i + seg] = lp(n[i:i + seg], fc)
    return out * np.sin(np.pi * sw) ** 1.5
def pop(f=520):
    t = t_arr(0.12); fr = f * (1 + 1.5 * np.exp(-t * 60))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 28)
def thud():
    t = t_arr(0.3); return np.sin(2 * np.pi * np.cumsum(90 * np.exp(-t * 10) + 40) / SR) * np.exp(-t * 14) + 0.2 * lp(rng.standard_normal(len(t)), 600) * np.exp(-t * 30)
def ding(f=1318.5):
    t = t_arr(0.9); return (np.sin(2 * np.pi * f * t) + 0.4 * np.sin(2 * np.pi * f * 2.01 * t)) * np.exp(-t * 4.5)
def buzz():
    t = t_arr(0.28); s = np.sign(np.sin(2 * np.pi * 150 * t)) * 0.5 + np.sin(2 * np.pi * 155 * t) * 0.5
    return lp(s, 1800) * env(len(t), 0.005, 0.08)
def click():
    t = t_arr(0.03); return hp(rng.standard_normal(len(t)), 2500) * np.exp(-t * 200)
def tick():
    t = t_arr(0.05); return np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 120)
# transições
for tb in (3.30, 6.90, 11.30, 15.30): add(sfx, tb, whoosh(0.5), 0.35)
# cena 1
add(sfx, 0.40, thud(), 0.5)
add(sfx, 0.60, pop(520), 0.3)          # telemóvel
add(sfx, 1.95, click(), 0.6); add(sfx, 1.97, pop(700), 0.35)   # carrega no botão
add(sfx, 2.00, whoosh(0.35), 0.15)     # ripple
# cena 2 MITO
add(sfx, 3.45, thud(), 0.75); add(sfx, 3.45, buzz(), 0.22)
add(sfx, 4.05, pop(520), 0.25)
# cena 3 tabela
add(sfx, 7.55, pop(420), 0.35)
for i in range(4):
    a = 8.15 + i * 0.55
    add(sfx, a, buzz(), 0.2, pan=-0.2)
    add(sfx, a + 0.22, ding(1318.5 + i * 110), 0.28, pan=0.2)
# cena 4 contador
add(sfx, 11.95, pop(420), 0.35)
for k in range(12): add(sfx, 12.15 + k * 0.1, tick(), 0.10 + k * 0.01)
add(sfx, 13.45, whoosh(0.3, up=False), 0.15)   # seta
add(sfx, 13.75, thud(), 0.6); add(sfx, 13.75, buzz(), 0.3)   # 1 mensagem
add(sfx, 14.25, pop(600), 0.2)
# cena 5 CTA
add(sfx, 16.25, whoosh(0.4), 0.2)
for k in range(7): add(sfx, 16.65 + k * 0.1, click(), 0.35, pan=0.1)
add(sfx, 17.45, pop(660), 0.4); add(sfx, 17.50, ding(1760.0), 0.25)

mix = music + sfx
mix /= np.max(np.abs(mix)) * 1.12
wavfile.write("som.wav", SR, (mix * 32767).astype(np.int16))
print("ok", mix.shape)
