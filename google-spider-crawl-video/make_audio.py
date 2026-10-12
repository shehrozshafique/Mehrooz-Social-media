"""Synthesizes the soundtrack for animation.html: a dark synth beat plus
sound effects timed to the on-screen events. Writes output/soundtrack.wav.
Usage: python3 make_audio.py
"""
import os
import wave

import numpy as np

SR = 44100
DUR = 44.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
music = np.zeros((N, 2))
sfx = np.zeros((N, 2))


def t_axis(d):
    return np.arange(int(d * SR)) / SR


def env(n, a=0.005, r=0.1):
    e = np.ones(n)
    na, nr = max(1, int(a * SR)), max(1, int(r * SR))
    e[:na] = np.linspace(0, 1, na)
    if nr < n:
        e[-nr:] *= np.linspace(1, 0, nr)
    return e


def add(buf, start, sig, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N:
        return
    sig = sig[: N - i] * gain
    buf[i:i + len(sig), 0] += sig * (1 - pan) ** 0.5 if pan > 0 else sig
    buf[i:i + len(sig), 1] += sig * (1 + pan) ** 0.5 if pan < 0 else sig


def lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for k in range(len(x)):
        acc = (1 - a) * x[k] + a * acc
        y[k] = acc
    return y


def note(f):
    return 440.0 * 2 ** ((f - 69) / 12)


# ---------- instruments ----------
def kick():
    t = t_axis(0.35)
    f = 50 + 110 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)


def hat(open_=False):
    t = t_axis(0.18 if open_ else 0.05)
    n = rng.standard_normal(len(t))
    n = n - lowpass(n, 6000)
    return n * np.exp(-t * (18 if open_ else 70)) * 0.5


def clap():
    t = t_axis(0.2)
    n = rng.standard_normal(len(t))
    n = n - lowpass(n, 1200)
    e = np.exp(-t * 25) + 0.6 * np.exp(-np.maximum(t - 0.012, 0) * 30) * (t > 0.012)
    return n * e * 0.5


def bass(freq, d):
    t = t_axis(d)
    saw = 2 * ((t * freq) % 1) - 1
    s = lowpass(saw, 380) + 0.5 * np.sin(2 * np.pi * freq * t)
    return s * env(len(t), 0.005, 0.08)


def pad(freqs, d):
    t = t_axis(d)
    s = np.zeros(len(t))
    for f in freqs:
        for det in (-0.12, 0.0, 0.12):
            s += np.sin(2 * np.pi * f * (1 + det / 100) * t + rng.random() * 6)
    return s / (len(freqs) * 3) * env(len(t), 0.6, 0.8)


def blip(freq, d=0.12, decay=30):
    t = t_axis(d)
    return (np.sin(2 * np.pi * freq * t) + 0.3 * np.sin(4 * np.pi * freq * t)) * np.exp(-t * decay) * env(len(t), 0.002, 0.02)


def whoosh(d=0.6, up=True):
    t = t_axis(d)
    n = rng.standard_normal(len(t))
    cut = np.linspace(400, 5000, len(t)) if up else np.linspace(5000, 400, len(t))
    # crude swept lowpass: blend between two filtered versions
    lo, hi = lowpass(n, 500), lowpass(n, 5000)
    m = (cut - 400) / 4600
    s = lo * (1 - m) + hi * m
    shape = np.sin(np.pi * np.linspace(0, 1, len(t))) ** 2
    return s * shape * 0.6


def impact():
    t = t_axis(0.9)
    f = 40 + 80 * np.exp(-t * 12)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 4)
    n = lowpass(rng.standard_normal(len(t)), 2500) * np.exp(-t * 10) * 0.6
    return body + n


def tick():
    t = t_axis(0.025)
    n = rng.standard_normal(len(t))
    return (n - lowpass(n, 3000)) * np.exp(-t * 200) * 0.6


def buzz(freq=110, d=0.35):
    t = t_axis(d)
    sq = np.sign(np.sin(2 * np.pi * freq * t)) + np.sign(np.sin(2 * np.pi * freq * 1.02 * t))
    return lowpass(sq, 1500) * 0.35 * env(len(t), 0.005, 0.1)


def chime(freqs, d=0.8):
    t = t_axis(d)
    s = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * 5) for f in freqs)
    return s / len(freqs) * env(len(t), 0.003, 0.2)


def riser(d, f0=200, f1=1600):
    t = t_axis(d)
    f = np.geomspace(f0, f1, len(t))
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.5
    return s * np.linspace(0, 1, len(t)) ** 2


# ---------- music: 120 BPM, A minor (Am - F - C - G) ----------
BEAT = 0.5
chords = [(57, 60, 64), (53, 57, 60), (48, 52, 55), (55, 59, 62)]
roots = [33, 29, 36, 31]
MUSIC_START, DROP_END = 1.6, 40.6
for bar in range(int(DUR / (4 * BEAT)) + 1):
    t0 = bar * 4 * BEAT
    ci = bar % 4
    if t0 < DUR - 1:
        add(music, t0, pad([note(n) for n in chords[ci]], 4 * BEAT + 0.6), 0.22)
    if MUSIC_START - 0.01 <= t0 < DROP_END:
        for b in range(4):
            tb = t0 + b * BEAT
            if tb >= DROP_END:
                break
            add(music, tb, kick(), 0.9)
            if b in (1, 3):
                add(music, tb, clap(), 0.35, pan=0.1)
            for h in range(2):
                add(music, tb + h * BEAT / 2, hat(open_=(h == 1 and b == 3)), 0.22, pan=-0.3 if h else 0.3)
            for e in range(2):
                n = roots[ci] + (12 if (b * 2 + e) % 4 == 3 else 0)
                add(music, tb + e * BEAT / 2, bass(note(n), BEAT / 2 - 0.02), 0.32)
# outro: sustained chord after the drop
add(music, DROP_END, pad([note(n) for n in (57, 60, 64, 69)], DUR - DROP_END), 0.35)

# ---------- sound effects, timed to animation.html ----------
add(sfx, 0.0, riser(1.6, 120, 900), 0.25)
for i, st in enumerate((0.7, 1.0, 1.3)):
    add(sfx, st, impact(), 0.55 if i == 1 else 0.35)
for i in range(4):
    add(sfx, 2.4 + i * 0.3, blip(note(76 + i * 2)), 0.3)

for st in (4.5, 11.0, 21.4, 28.4, 35.4):
    add(sfx, st - 0.3, whoosh(0.7), 0.4)

# scene 2: discover
A = 4.5
for i in range(3):
    add(sfx, A + 0.4 + i * 0.2, blip(note(72 + i * 3), 0.15), 0.25, pan=(i - 1) * 0.5)
for i in range(6):
    add(sfx, A + 1.3 + i * 0.32, blip(note(84), 0.06, 60), 0.18)
for i, s in enumerate(['# robots.txt', 'User-agent: Googlebot', 'Allow: /', 'Disallow: /admin']):
    st = A + 3.5 + i * 0.35
    for k in range(0, len(s), 2):
        add(sfx, st + 0.35 * k / len(s), tick(), 0.25)
add(sfx, A + 5.0, buzz(90, 0.4), 0.45)
add(sfx, A + 5.3, chime([note(79), note(83), note(86)], 0.7), 0.25)

# scene 3: crawl graph (matches nodes[] / visit timing)
statuses = [200, 200, 200, 200, 200, 404, 200, 301, 200, 200, 200]
add(sfx, 11.8, blip(note(72), 0.2), 0.35)
for i in range(1, 11):
    vt = 12.2 + (i - 1) * 0.8
    add(sfx, vt + 0.2, tick(), 0.2)
    lit = vt + 0.8 * 0.85
    if statuses[i] == 404:
        add(sfx, lit, buzz(80, 0.35), 0.45)
    elif statuses[i] == 301:
        add(sfx, lit, blip(note(79), 0.12), 0.3)
        add(sfx, lit + 0.1, blip(note(74), 0.15), 0.3)
    else:
        add(sfx, lit, blip(note(72 + (i * 2) % 12), 0.15), 0.32, pan=0.3 * np.sin(i))
add(sfx, 20.3, chime([note(62), note(65)], 0.9), 0.35)

# scene 4: render
A = 21.4
lines = ['<html>', '  <head><title>JS SEO</title></head>', '  <body>', '    <div id="app"></div>',
         '    <script src="app.js"></script>', '  </body>', '</html>']
for i, s in enumerate(lines):
    st = A + 0.7 + i * 0.25
    for k in range(0, len(s), 4):
        add(sfx, st + 0.3 * k / len(s), tick(), 0.18)
add(sfx, A + 2.7, blip(note(67), 0.2, 15), 0.35)
add(sfx, A + 3.3, riser(1.1, 300, 1200), 0.18)
add(sfx, A + 4.4, chime([note(76), note(79), note(84)], 0.8), 0.3)
for k in range(5):
    add(sfx, A + 4.6 + k * 0.3, blip(note(79 + k), 0.08, 50), 0.2)

# scene 5: index stamps
A = 28.4
for i in range(9):
    add(sfx, A + 0.4 + i * 0.22, whoosh(0.18), 0.12)
    good = i < 5
    add(sfx, A + 2.7 + i * 0.22, kick()[: int(0.12 * SR)], 0.4)
    add(sfx, A + 2.7 + i * 0.22, blip(note(81) if good else note(57), 0.1, 40), 0.25 if good else 0.3)
for k in range(6):
    add(sfx, A + 4.8 + k * 0.14, blip(note(84 + k), 0.06, 60), 0.2)

# scene 6: checklist + CTA
A = 35.4
for i in range(5):
    add(sfx, A + 0.7 + i * 0.45, chime([note(76 + i * 2), note(83 + i * 2)], 0.5), 0.28)
add(sfx, 40.1, riser(0.6, 300, 2000), 0.25)
add(sfx, 40.7, impact(), 0.75)
add(sfx, 40.7, chime([note(69), note(76), note(81), note(88)], 2.5), 0.3)
add(sfx, 41.8, blip(note(88), 0.25, 12), 0.3)

# simple stereo echo on effects for space
d = int(0.18 * SR)
echo = np.zeros_like(sfx)
echo[d:, 0] = sfx[:-d, 1] * 0.25
echo[d:, 1] = sfx[:-d, 0] * 0.25
mix = music * 0.55 + sfx + echo

# fades + soft clip
fade_in, fade_out = int(0.3 * SR), int(1.5 * SR)
mix[:fade_in] *= np.linspace(0, 1, fade_in)[:, None]
mix[-fade_out:] *= np.linspace(1, 0, fade_out)[:, None]
mix = np.tanh(mix * 1.1)
mix /= np.max(np.abs(mix)) / 0.89

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output', 'soundtrack.wav')
os.makedirs(os.path.dirname(out), exist_ok=True)
with wave.open(out, 'wb') as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype('<i2').tobytes())
print('wrote', out)
