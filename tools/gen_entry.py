#!/usr/bin/env python3
"""Rebuild the Friday 20 November 2026 world-news front page.

Offline, deterministic, local fonts only. 1024x1024 PNG.
Original drawn reportage: every illustration below is generated from
vector primitives (no photographs, no copied artwork, no network assets).
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os
import sys

W = H = 1024
M = 36
CW = W - 2 * M

PAPER = (241, 235, 222)
INK = (22, 19, 15)
RED = (190, 45, 38)
RED_D = (150, 32, 28)
PETROL = (18, 50, 58)
PETROL2 = (26, 66, 74)
PETROL3 = (48, 92, 98)
LAND = (24, 70, 66)
CREAM = (241, 235, 222)
MUTED = (108, 100, 86)
FAINT = (198, 190, 174)
TINT = (226, 217, 200)
AMBER = (222, 150, 54)
GREEN = (40, 96, 80)

FONT_DIR = "/usr/share/fonts/truetype/sand-box"
SERIF = f"{FONT_DIR}/custom/Source Serif Pro/SourceSerifPro-Regular.ttf"
SERIF_SB = f"{FONT_DIR}/custom/Source Serif Pro/SourceSerifPro-Semibold.ttf"
SERIF_IT = f"{FONT_DIR}/custom/Source Serif Pro/SourceSerifPro-It.ttf"
BC_BLACK = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-Black.ttf"
BC_XB = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-ExtraBold.ttf"
BC_B = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-Bold.ttf"
BC_SB = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-SemiBold.ttf"
BC_M = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-Medium.ttf"

_fc = {}


def F(path, size):
    key = (path, size)
    if key not in _fc:
        _fc[key] = ImageFont.truetype(path, size)
    return _fc[key]


AUDIT = []


def text(d, xy, s, font, fill=INK, anchor="la"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)
    try:
        AUDIT.append((d.textbbox(xy, s, font=font, anchor=anchor), s))
    except Exception:
        pass


def tracked(d, xy, s, font, fill=INK, tracking=0.0):
    x, y = xy
    for ch in s:
        text(d, (x, y), ch, font, fill)
        x += font.getlength(ch) + tracking
    return x


def rule(d, x1, y1, x2, y2, width=1, fill=INK):
    if width <= 1:
        d.rectangle([int(x1), int(y1), int(x2), int(y2)], fill=fill)
    else:
        d.line([x1, y1, x2, y2], fill=fill, width=width)


def wrap(s, font, maxw):
    words = s.split()
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if font.getlength(trial) <= maxw:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            if font.getlength(word) > maxw:
                part = ""
                for ch in word:
                    if font.getlength(part + ch) <= maxw:
                        part += ch
                    else:
                        if part:
                            lines.append(part)
                        part = ch
                cur = part
            else:
                cur = word
    if cur:
        lines.append(cur)
    return lines


def fit(s, font, maxw):
    if font.getlength(s) <= maxw:
        return s
    while s and font.getlength(s + "…") > maxw:
        s = s[:-1]
    return s.rstrip(" ,.;:-") + "…"


def draw_para(d, s, font, x, y, maxw, lh, fill=INK, justify=False,
              max_lines=None, anchor="la"):
    lines = wrap(s, font, maxw)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and font.getlength(last + "…") > maxw:
            last = last[:-1]
        lines[-1] = last.rstrip(" ,.;:") + "…"
    for i, line in enumerate(lines):
        if justify and i < len(lines) - 1 and " " in line:
            words = line.split(" ")
            word_w = sum(font.getlength(w) for w in words)
            space_w = font.getlength(" ")
            extra = maxw - word_w - space_w * (len(words) - 1)
            if extra > 0:
                step = space_w + extra / (len(words) - 1)
                xx = x
                for j, w in enumerate(words):
                    text(d, (xx, y), w, font, fill, anchor)
                    xx += font.getlength(w) + (step if j < len(words) - 1 else 0)
                y += lh
                continue
        text(d, (x, y), line, font, fill, anchor)
        y += lh
    return y, lines


def badge(d, x, y, n, r=8):
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED)
    text(d, (x, y), str(n), F(BC_B, 9), CREAM, anchor="mm")


def tag(d, x, y, label, fill=RED, size=6.0):
    f = F(BC_SB, size)
    wd = f.getlength(label) + 10
    d.rectangle([x, y, x + wd, y + 10], fill=fill)
    text(d, (x + 5, y + 4.7), label, f, CREAM)
    return wd


# ============================================================ illustrations
def illus_cyclone(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for yy in range(y + 14, y + h - 6, 15):
        for k in range(9):
            sx = x + int(w * 0.40) + k * 38
            d.arc([sx, yy, sx + 26, yy + 9], 200, 340, fill=PETROL3)
    coast = [(x + int(w * .44), y), (x + int(w * .43), y + 24),
             (x + int(w * .39), y + 48), (x + int(w * .35), y + 72),
             (x + int(w * .31), y + 96), (x + int(w * .27), y + 120),
             (x + int(w * .23), y + h)]
    d.polygon([(x, y)] + coast + [(x, y + h)], fill=LAND)
    d.line(coast, fill=CREAM, width=2, joint="curve")
    for i in range(10):
        for j in range(5):
            rx, ry = x + 12 + i * 20, y + 14 + j * 27
            d.line([(rx, ry), (rx - 6, ry + 11)], fill=(88, 128, 128))
    cx, cy = x + int(w * .70), y + int(h * .44)
    sp = []
    for i in range(170):
        t = i / 169 * 2 * math.pi * 2.6
        r = 5 + 36 * (i / 169)
        sp.append((cx + r * math.cos(t), cy + .64 * r * math.sin(t)))
    d.line(sp, fill=CREAM, width=1, joint="curve")
    for rr in (50, 68, 86):
        d.arc([cx - rr, cy - int(rr * .62), cx + rr, cy + int(rr * .62)],
              205, 335, fill=PETROL3)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=RED)
    # dashed track heading into the coast
    tx0, ty0 = x + w - 16, y + h - 30
    tx1, ty1 = x + int(w * .35), y + 72
    for i in range(0, 18, 2):
        p0 = (tx0 + (tx1 - tx0) * i / 18, ty0 + (ty1 - ty0) * i / 18)
        p1 = (tx0 + (tx1 - tx0) * (i + 1) / 18, ty0 + (ty1 - ty0) * (i + 1) / 18)
        d.line([p0, p1], fill=RED, width=2)
    lx, ly = x + int(w * .35), y + 72
    d.ellipse([lx - 7, ly - 7, lx + 7, ly + 7], outline=CREAM, width=1)
    d.ellipse([lx - 3, ly - 3, lx + 3, ly + 3], fill=RED)
    # two little shelters with evacuation arrows
    for i in range(2):
        hx, hy = x + 16 + i * 30, y + h - 56
        d.polygon([(hx, hy + 5), (hx + 6, hy), (hx + 12, hy + 5)], outline=CREAM)
        d.rectangle([hx + 2, hy + 5, hx + 10, hy + 12], outline=CREAM)
        d.line([(hx + 16, hy + 9), (hx + 26, hy + 9)], fill=AMBER, width=1)
        d.line([(hx + 22, hy + 5), (hx + 26, hy + 9), (hx + 22, hy + 13)],
               fill=AMBER, width=1)
    text(d, (x + 12, y + 10), "INDIA", F(BC_B, 9), CREAM)
    text(d, (x + 14, y + 30), "ODISHA", F(BC_SB, 7), CREAM)
    text(d, (x + int(w * .60), y + h - 62), "BAY OF", F(BC_SB, 8), CREAM)
    text(d, (x + int(w * .60), y + h - 52), "BENGAL", F(BC_SB, 8), CREAM)
    text(d, (lx + 10, ly - 4), "GOPALPUR", F(BC_B, 7), CREAM)
    text(d, (x + int(w * .63), y + 10), "CYCLONE AKVAN", F(BC_B, 7.5), AMBER)
    # caption strip
    cy0 = y + h - 18
    d.rectangle([x, cy0, x + w, y + h], fill=(10, 34, 40))
    text(d, (x + 10, cy0 + 2), "IMD  ·  LANDFALL 07:30–08:30 IST  ·  3.72 LAKH EVACUATED  ·  NO MAJOR DEATH TOLL REPORTED",
         F(BC_SB, 6.8), CREAM)


def illus_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for i in range(26):
        sx = x + (i * 47) % w
        sy = y + (i * 29) % (h - 20)
        d.ellipse([sx, sy, sx + 1, sy + 1], fill=PETROL3)
    base = y + h - 8
    skyline = [(0, 34), (18, 34), (18, 20), (34, 20), (34, 44), (52, 44),
               (52, 14), (66, 14), (66, 38), (82, 38), (82, 26), (104, 26),
               (104, 48), (122, 48), (122, 8), (136, 8), (136, 40), (152, 40),
               (152, 22), (170, 22), (170, 46), (188, 46), (188, 30), (210, 30),
               (210, 18), (226, 18), (226, 42), (244, 42), (244, 12), (258, 12),
               (258, 46), (280, 46), (280, 28), (300, 28)]
    pts = [(x + a, base - b) for a, b in skyline]
    d.polygon([(x, base)] + pts + [(x + w, base)], fill=(11, 33, 40))
    d.line(pts, fill=(120, 150, 150), width=1)
    for i in range(9):
        wx = x + 22 + i * 31
        wy = base - (18 + (i * 7) % 18)
        d.rectangle([wx, wy, wx + 3, wy + 4], fill=AMBER if i % 3 else (92, 124, 120))
    # missile arcs
    for i in range(4):
        sx = x + w - 20 - i * 16
        ex = x + 40 + i * 58
        d.line([(sx, y + 4), (ex, base - 14 - i * 5)], fill=RED, width=2)
        d.polygon([(ex, base - 14 - i * 5), (ex - 5, base - 22 - i * 5),
                   (ex - 1, base - 20 - i * 5)], fill=RED)
    # explosions
    for ex, ey, r in ((x + 96, base - 30, 12), (x + 214, base - 44, 9)):
        d.ellipse([ex - r, ey - r, ex + r, ey + r], fill=AMBER)
        for a in range(0, 360, 45):
            ra = math.radians(a)
            d.line([(ex + (r + 2) * math.cos(ra), ey + (r + 2) * math.sin(ra)),
                    (ex + (r + 8) * math.cos(ra), ey + (r + 8) * math.sin(ra))],
                   fill=RED, width=2)
    d.rectangle([x, y, x + w, y + 16], fill=(10, 30, 36))
    text(d, (x + 10, y + 3), "~30 BALLISTIC MISSILES  ·  ENERGY, TRANSPORT, EMBASSIES HIT",
         F(BC_SB, 7.0), CREAM)


def illus_cop(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=GREEN)
    # globe
    gx, gy, gr = x + 74, y + 58, 34
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=CREAM, width=2)
    d.arc([gx - gr, gy - 12, gx + gr, gy + 12], 0, 360, fill=(120, 160, 140))
    d.arc([gx - 13, gy - gr, gx + 13, gy + gr], 0, 360, fill=(120, 160, 140))
    d.line([(gx - gr, gy), (gx + gr, gy)], fill=(120, 160, 140))
    for ang in (30, 150, 260):
        a = math.radians(ang)
        d.ellipse([gx + gr * math.cos(a) - 6, gy + gr * math.sin(a) - 4,
                   gx + gr * math.cos(a) + 6, gy + gr * math.sin(a) + 4],
                  fill=(150, 184, 150))
    # thermometer
    tx = x + 148
    d.rounded_rectangle([tx - 5, y + 14, tx + 5, y + 70], radius=5,
                        outline=CREAM, width=2)
    d.ellipse([tx - 10, y + 62, tx + 10, y + 82], fill=RED)
    d.rectangle([tx - 2, y + 30, tx + 2, y + 68], fill=RED)
    for ty in (y + 22, y + 38, y + 54):
        d.line([(tx + 6, ty), (tx + 12, ty)], fill=CREAM)
    # deadlock: two facing empty chairs
    for cxx in (x + 208, x + 262):
        d.line([(cxx - 12, y + 66), (cxx - 12, y + 42), (cxx + 12, y + 42),
                (cxx + 12, y + 66)], fill=CREAM, width=2)
        d.line([(cxx - 12, y + 54), (cxx + 12, y + 54)], fill=(120, 160, 140))
    d.line([(x + 226, y + 50), (x + 244, y + 50)], fill=RED, width=2)
    # clock near midnight
    kx, ky = x + w - 30, y + 24
    d.ellipse([kx - 14, ky - 14, kx + 14, ky + 14], outline=AMBER, width=2)
    d.line([(kx, ky), (kx, ky - 9)], fill=AMBER, width=2)
    d.line([(kx, ky), (kx + 7, ky + 5)], fill=AMBER, width=2)
    d.rectangle([x, y, x + w, y + 16], fill=(24, 66, 58))
    text(d, (x + 10, y + 3), "ANTALYA  ·  FINAL DAY  ·  $120BN FINANCE GAP UNRESOLVED",
         F(BC_SB, 7.0), CREAM)


def illus_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for gx in range(x + 16, x + w, 26):
        d.line([(gx, y + 20), (gx, y + h - 14)], fill=PETROL2)
    for gy in range(y + 26, y + h - 10, 18):
        d.line([(x + 12, gy), (x + w - 12, gy)], fill=PETROL2)
    n = 12
    for i in range(n):
        cx = x + 24 + i * ((w - 56) / n)
        top = y + 24 + i * 4.6
        bot = top + 16 + (i % 3) * 3
        d.line([(cx, top), (cx, bot)], fill=RED, width=2)
        d.rectangle([cx - 4, top + 5, cx + 4, bot - 4], fill=RED if i % 2 else RED_D)
    # falling arrow
    ax0, ay0 = x + w - 96, y + 30
    ax1, ay1 = x + 34, y + h - 26
    d.line([(ax0, ay0), (ax1, ay1)], fill=AMBER, width=3)
    d.polygon([(ax1, ay1), (ax1 + 12, ay1 - 2), (ax1 + 2, ay1 - 13)], fill=AMBER)
    # chip glyph
    cs = 14
    chx, chy = x + w - 30, y + h - 32
    d.rectangle([chx - cs, chy - cs, chx + cs, chy + cs], outline=GREEN, width=2)
    d.rectangle([chx - 6, chy - 6, chx + 6, chy + 6], fill=GREEN)
    for s in range(-8, 9, 5):
        d.line([(chx - cs, chy + s), (chx - cs - 4, chy + s)], fill=GREEN)
        d.line([(chx + cs, chy + s), (chx + cs + 4, chy + s)], fill=GREEN)
    d.rectangle([x, y, x + w, y + 16], fill=(10, 30, 36))
    text(d, (x + 10, y + 3), "TOKYO · SEOUL · CHIP VALUATIONS RESET",
         F(BC_SB, 7.0), CREAM)


def illus_mercury(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for i in range(18):
        sx = x + (i * 41) % w
        sy = y + (i * 23) % h
        d.ellipse([sx, sy, sx + 1, sy + 1], fill=CREAM)
    px, py, pr = x + int(w * .68), y + int(h * .54), int(min(w, h) * .34)
    d.ellipse([px - pr, py - pr, px + pr, py + pr], fill=(96, 92, 82))
    for a in range(0, 360, 60):
        ra = math.radians(a)
        ccx, ccy = px + pr * .5 * math.cos(ra), py + pr * .5 * math.sin(ra)
        d.ellipse([ccx - 5, ccy - 4, ccx + 5, ccy + 4], fill=(74, 70, 62))
    d.arc([px - pr - 8, py - pr - 8, px + pr + 8, py + pr + 8], 200, 340,
          fill=AMBER, width=1)
    # spacecraft: body + two solar wings
    sx, sy = x + 28, y + 30
    d.polygon([(sx, sy), (sx + 16, sy + 5), (sx + 14, sy + 15), (sx, sy + 11)],
              fill=CREAM)
    d.ellipse([sx + 12, sy + 4, sx + 20, sy + 12], outline=AMBER, width=2)
    for k in range(3):
        d.line([(sx - 2 - k * 7, sy + 2), (sx - 2 - k * 7, sy + 10)], fill=(110, 150, 154))
        d.line([(sx - 20, sy + 2 + k * 3), (sx - 9, sy + 2 + k * 3)], fill=(110, 150, 154))
    d.line([(sx + 20, sy + 8), (px - pr - 2, py - 8)], fill=AMBER)


def illus_boat(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for k in range(4):
        wy = y + 26 + k * 11
        d.arc([x + 4, wy, x + w - 4, wy + 9], 200, 340, fill=PETROL3)
    # tilting hull
    d.polygon([(x + 18, y + 36), (x + 62, y + 30), (x + 56, y + 44),
               (x + 26, y + 46)], fill=AMBER)
    d.line([(x + 18, y + 36), (x + 62, y + 30)], fill=CREAM, width=2)
    for i in range(3):
        hx = x + 30 + i * 10
        d.ellipse([hx, y + 22, hx + 5, y + 27], fill=CREAM)
        d.line([(hx + 2, y + 27), (hx + 2, y + 34)], fill=CREAM, width=2)
    # rescue beacon + ray
    bx, by = x + 52, y + 22
    d.line([(bx, by), (bx, by - 12)], fill=RED, width=2)
    d.ellipse([bx - 2, by - 16, bx + 2, by - 12], fill=RED)
    for a in (150, 180, 210):
        ra = math.radians(a)
        d.line([(bx, by - 14), (bx + 14 * math.cos(ra), by - 14 + 14 * math.sin(ra))],
               fill=RED)


def illus_blast(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL2)
    d.rectangle([x + 14, y + 20, x + 54, y + h - 4], fill=(70, 76, 72))
    d.rectangle([x + 58, y + 28, x + 84, y + h - 4], fill=(56, 64, 62))
    for r in range(3):
        for c in range(2):
            d.rectangle([x + 18 + c * 16, y + 26 + r * 12, x + 25 + c * 16, y + 32 + r * 12],
                        fill=(150, 150, 130))
    # collapsed corner
    d.polygon([(x + 58, y + h - 4), (x + 58, y + 46), (x + 72, y + 56),
               (x + 84, y + h - 4)], fill=(34, 38, 36))
    for i in range(4):
        sx = x + 62 + i * 7
        d.line([(sx, y + h - 4), (sx + 4, y + h - 14)], fill=(120, 110, 96))
    # smoke
    for i in range(5):
        sx, sy, r = x + 40 + i * 9, y + 14 - (i % 2) * 6, 8 + (i % 3) * 3
        d.ellipse([sx - r, sy - r, sx + r, sy + r], fill=(104, 100, 92))


def illus_debt(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    gx, gy, gr = x + 34, y + int(h * .55), int(min(w, h) * .38)
    d.ellipse([gx - gr, gy - gr, gx + gr, gy + gr], outline=CREAM, width=1)
    d.arc([gx - gr, gy - 10, gx + gr, gy + 10], 0, 360, fill=PETROL3)
    d.line([(gx, gy - gr), (gx, gy + gr)], fill=PETROL3)
    # rising curve breaking the circle
    pts = [(x + 20, y + h - 14), (x + 40, y + h - 24), (x + 58, y + h - 20),
           (x + 76, y + h - 40), (x + w - 14, y + 16)]
    d.line(pts, fill=RED, width=3, joint="curve")
    d.polygon([(pts[-1][0] - 9, pts[-1][1] + 2), pts[-1],
               (pts[-1][0] - 1, pts[-1][1] + 10)], fill=RED)
    text(d, (x + w - 50, y + 30), "100%", F(BC_XB, 15), AMBER)


def illus_tanker(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for k in range(3):
        wy = y + 36 + k * 10
        d.arc([x + 4, wy, x + w - 4, wy + 8], 200, 340, fill=PETROL3)
    # hull
    d.polygon([(x + 10, y + 34), (x + 62, y + 34), (x + 56, y + 44),
               (x + 18, y + 44)], fill=(92, 98, 92))
    d.rectangle([x + 22, y + 26, x + 48, y + 34], fill=(70, 76, 72))
    # fire plume
    d.polygon([(x + 32, y + 26), (x + 38, y + 8), (x + 44, y + 26)], fill=AMBER)
    d.polygon([(x + 35, y + 26), (x + 39, y + 14), (x + 43, y + 26)], fill=RED)
    for r in (18, 28):
        d.arc([x + 39 - r, y + 20 - r, x + 39 + r, y + 20 + r], 200, 340,
              fill=RED)


def illus_strike(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=RED_D)
    d.rectangle([x, y, x + w, y + 14], fill=(120, 28, 26))
    text(d, (x + 8, y + 3), "24-HOUR GENERAL STRIKE", F(BC_SB, 7), CREAM)
    for i in range(6):
        fx = x + 14 + i * 20
        fy = y + 30 + (i % 2) * 6
        d.line([(fx, fy + 16), (fx, fy)], fill=CREAM, width=3)
        d.ellipse([fx - 4, fy - 6, fx + 4, fy + 2], fill=CREAM)
        d.line([(fx - 4, fy + 2), (fx - 8, fy - 4)], fill=CREAM, width=2)
        d.line([(fx + 4, fy + 2), (fx + 8, fy - 4)], fill=CREAM, width=2)


def illus_brazil(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=GREEN)
    for i in range(5):
        tx = x + 12 + i * 28
        d.polygon([(tx, y + h - 4), (tx + 10, y + 20), (tx + 20, y + h - 4)],
                  fill=(28, 74, 56))
        d.ellipse([tx - 6, y + 12, tx + 26, y + 34], fill=(52, 112, 70))
    # flag
    fx = x + w - 30
    d.line([(fx, y + 8), (fx, y + h - 6)], fill=CREAM)
    d.rectangle([fx, y + 8, fx + 26, y + 24], fill=(30, 90, 56))
    d.polygon([(fx + 13, y + 11), (fx + 21, y + 16), (fx + 13, y + 21)], fill=AMBER)


def illus_mine(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL2)
    hx = x + 38
    d.line([(hx - 12, y + h - 6), (hx, y + 12), (hx + 12, y + h - 6)], fill=CREAM, width=2)
    d.line([(hx - 15, y + 16), (hx + 15, y + 16)], fill=CREAM, width=2)
    d.line([(hx, y + 12), (hx, y + h - 6)], fill=(120, 150, 150))
    d.polygon([(x + 56, y + h - 6), (x + 72, y + 26), (x + w - 6, y + h - 6)],
              fill=(84, 74, 58))
    d.rectangle([x + 8, y + h - 10, x + w - 4, y + h - 5], fill=(60, 60, 50))


def illus_cpi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    by = y + h - 12
    d.line([(x + 10, by), (x + w - 8, by)], fill=PETROL3)
    for i, ht in enumerate((16, 22, 20, 26, 30, 34)):
        bx = x + 14 + i * 22
        d.rectangle([bx, by - ht, bx + 13, by], fill=AMBER if i < 4 else RED)
    text(d, (x + 12, y + 8), "2.3%", F(BC_XB, 17), CREAM)
    d.line([(x + w - 44, y + 14), (x + w - 10, y + 14)], fill=RED, width=2)


def illus_rates(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for i, (lab, frac) in enumerate((("1Y  3.0%", .62), ("5Y  3.5%", .72))):
        yy = y + 22 + i * 24
        text(d, (x + 10, yy - 4), lab, F(BC_SB, 8), CREAM)
        d.rectangle([x + 10, yy + 8, x + w - 12, yy + 13], fill=PETROL2)
        d.rectangle([x + 10, yy + 8, x + int((w - 24) * frac), yy + 13], fill=AMBER)
    d.line([(x + 10, y + h - 10), (x + w - 12, y + h - 10)], fill=RED, width=2)


# ============================================================ content
STATS = [
    ("3.72 LAKH", "evacuated in Odisha", "ODISHA"),
    ("~30", "missiles fired at Kyiv", "EUROPE"),
    ("$120BN", "COP31 finance gap", "CLIMATE"),
    ("2.3%", "Japan October core CPI", "ASIA"),
    ("3.0%", "China one-year LPR", "RATES"),
    ("8 YRS", "BepiColombo's voyage", "SPACE"),
]

REGIONS = [
    ("ASIA–PACIFIC", .24, RED), ("EUROPE", .18, PETROL2),
    ("MIDDLE EAST", .14, (160, 94, 40)), ("AFRICA", .10, GREEN),
    ("AMERICAS", .15, (120, 60, 70)), ("WORLD / SPACE", .19, PETROL3),
]

FEATURED = [
    dict(n=1, illus=illus_cyclone, tag="ODISHA · CYCLONE", tagc=RED,
         head="CYCLONE AKVAN COMES ASHORE IN INDIA",
         deck="Landfall near Gopalpur 7:30–8:30 am IST; winds 70–80 kmph, gusting 90; 3.72 lakh evacuated; Patrapur 209 mm. No major death toll reported at midday.",
         source="IMD / STATESMAN / INDIA TODAY", kind="lead"),
    dict(n=2, illus=illus_kyiv, tag="KYIV · WAR", tagc=RED,
         head="RUSSIAN MISSILE BARRAGE HITS KYIV",
         deck="About 30 missiles hit energy and transport sites; embassies damaged. Injuries reported in the repeat barrage after the Shenzhen talks.",
         source="REUTERS / KYIV CITY", kind="med"),
    dict(n=3, illus=illus_cop, tag="ANTALYA · CLIMATE", tagc=GREEN,
         head="COP31 REACHES FINAL DAY DEADLOCKED",
         deck="Final day in Antalya: the draft drops fossil-fuel language and a $120bn finance gap is unresolved. Overtime looks likely.",
         source="GUARDIAN / REUTERS", kind="med"),
    dict(n=4, illus=illus_markets, tag="TOKYO · MARKETS", tagc=RED,
         head="AI SELL-OFF SINKS ASIAN SHARES",
         source="REUTERS", kind="med"),
    dict(n=5, illus=illus_mercury, tag="SPACE", tagc=PETROL3,
         head="BepiColombo reaches Mercury", source="ESA", kind="small"),
    dict(n=6, illus=illus_boat, tag="SENEGAL · MIGRATION", tagc=GREEN,
         head="Migrant boat capsizes; four dead", source="AL JAZEERA", kind="small"),
    dict(n=7, illus=illus_blast, tag="GEORGIA", tagc=RED,
         head="Tbilisi gas blast kills six", source="SCMP / AFP", kind="small"),
    dict(n=8, illus=illus_debt, tag="IMF", tagc=RED,
         head="World debt nearing 100% of GDP", source="IMF", kind="small"),
    dict(n=9, illus=illus_tanker, tag="OMAN · SHIPPING", tagc=(160, 94, 40),
         head="Tanker struck near Oman; fire", source="UKMTO / REUTERS", kind="small"),
    dict(n=10, illus=illus_strike, tag="ROME · LABOUR", tagc=RED,
         head="Italy's CGIL holds general strike", source="CGIL / AFP", kind="small"),
    dict(n=11, illus=illus_brazil, tag="BRAZIL", tagc=GREEN,
         head="Lula meets Raoni on Indigenous land", source="AL JAZEERA", kind="small"),
    dict(n=12, illus=illus_mine, tag="OCEANIA", tagc=PETROL3,
         head="Rio Tinto pledges $70m for Panguna", source="REUTERS", kind="small"),
    dict(n=13, illus=illus_cpi, tag="TOKYO", tagc=RED,
         head="Japan's October CPI holds at 2.3%", source="REUTERS", kind="small"),
    dict(n=14, illus=illus_rates, tag="BEIJING", tagc=PETROL2,
         head="China holds lending rates 18th month", source="REUTERS", kind="small"),
]

BRIEFS = [
    ("Burnham opens first EU–UK reset summit", "EU COUNCIL"),
    ("Denmark backs Greenland defence bill", "AFP"),
    ("UK and Norway fund Ukraine's navy", "BBC"),
    ("France apartment fire kills one; 15 hurt", "AP"),
    ("Korea court clears ex-PM Han Duck-soo", "SBS"),
    ("Taiwan tightens short-selling curbs", "REUTERS"),
    ("Indonesia passes asset-forfeiture bill", "REUTERS"),
    ("Hong Kong temple-fire suspect held", "AP"),
    ("Austria beat South Africa 2–0, U17", "FIFA"),
    ("South Africa spin to Test victory", "ICC"),
    ("Uganda landslide survivors go to UN", "AP"),
    ("Somalia airstrike kills 13 militants", "AP"),
    ("Israel strikes Hezbollah site in Lebanon", "AP"),
    ("Mexico City marks Revolution Day", "AP"),
    ("Haiti police kill 34 gang suspects", "AP"),
    ("Bukele files for a third term in Salvador", "AP"),
    ("Fed minutes: most saw more tightening", "REUTERS"),
    ("IEA: data-centre emissions +70% by 2030", "IEA"),
    ("UN marks World Children's Day", "UN"),
    ("AUKUS sales could shrink US submarine fleet", "REUTERS"),
    ("Trial pill shrinks pancreatic tumours", "REUTERS"),
    ("Tonga and Fiji declare drought emergencies", "RNZ / AP"),
    ("China holds one-year LPR at 3.0%", "REUTERS"),
    ("Korea, Taiwan shares slip in chip sell-off", "REUTERS"),
]

DATE_CHECK = (
    "Excluded as Thursday 19 November news, not sold as Friday’s: the Trump–Xi–Putin Shenzhen summit and its "
    "four-point declaration; the ICJ Myanmar/Rohingya genocide judgment; the Houthi strike on Riyadh’s tallest "
    "tower; GTA VI’s launch-night sales; Anthropic’s Nasdaq debut; the Van Gogh sale; the US Senate Iran war-powers "
    "vote; and Trump’s Iran-strike delay. Friday papers may still mention them; they are not dated 20 November."
)

SOURCES = (
    "Sources: IMD; The Statesman; India Today; Reuters; AP; AFP; BBC; The Guardian; SCMP; Al Jazeera; ICC; FIFA; "
    "ESA; UN; IMF; IEA; EU Council; RNZ; SBS; UKMTO. Times and bulletins differ; COP31 was still in session at close."
)

# ============================================================ canvas
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# folio
tracked(d, (M, 15), "THE MERIDIAN", F(BC_B, 12.5), RED, 1.7)
text(d, (W - M, 16), "WORLD EDITION  ·  MORNING FINAL  ·  FRIDAY 20 NOVEMBER 2026",
     F(BC_M, 8.4), MUTED, anchor="ra")
rule(d, M, 33, W - M, 33, 1, INK)

# masthead
d.rectangle([M, 40, W - M, 55], fill=RED)
text(d, (M + 7, 42), "ONE DAY  ·  ONE PAGE  ·  SIX CONTINENTS  ·  ORIGINAL DRAWINGS",
     F(BC_SB, 7.6), CREAM)
text(d, (W - M - 7, 42), "NO. 326", F(BC_SB, 7.6), CREAM, anchor="ra")
mf = F(BC_BLACK, 80)
fw = mf.getlength("FRIDAY")
text(d, (M, 60), "FRIDAY", mf, RED)
text(d, (M + fw + 16, 60), "20 NOVEMBER 2026", mf, INK)
text(d, (M, 143),
     "The world in one day — Cyclone Akvan ashore in India · Russian missiles hit Kyiv · COP31’s final day · Asia’s AI sell-off",
     F(SERIF_IT, 12.2), INK)
text(d, (W - M, 144), "37 STORIES · 6 CONTINENTS", F(BC_SB, 7.4), MUTED, anchor="ra")
rule(d, M, 162, W - M, 162, 2, RED)

# stat rail
cell_w = CW / 6
for i, (big, lab, chip) in enumerate(STATS):
    cx = M + i * cell_w
    if i:
        rule(d, cx - 4, 168, cx - 4, 202, 1, FAINT)
    text(d, (cx + 2, 167), big, F(BC_XB, 21), INK)
    text(d, (cx + 2, 190), lab, F(SERIF, 7.4), MUTED)
    tag(d, cx + 2, 202, chip, fill=RED if i in (0, 1, 2, 3) else PETROL2, size=5.6)
rule(d, M, 214, W - M, 214, 1, INK)

# region bar
rx = M
for label, frac, col in REGIONS:
    rw = CW * frac
    d.rectangle([rx, 216, rx + rw - 2, 224], fill=col)
    text(d, (rx + 6, 217.3), label, F(BC_SB, 6.2), CREAM)
    rx += rw

# ------------------------------------------------------------- three leads
LEAD_Y0, LEAD_Y1 = 230, 430
lgap = 12
lw = (CW - 2 * lgap) // 3
lead_img_h = 104
for i, feat in enumerate(FEATURED[:3]):
    lx = M + i * (lw + lgap)
    d.rectangle([lx, LEAD_Y0, lx + lw, LEAD_Y1], outline=FAINT, width=1)
    feat["illus"](d, lx + 1, LEAD_Y0 + 1, lw - 2, lead_img_h)
    by = LEAD_Y0 + lead_img_h + 4
    badge(d, lx + 15, by + 9, feat["n"])
    tag(d, lx + 30, by + 4, feat["tag"], fill=feat["tagc"], size=6.0)
    text(d, (lx + lw - 9, by + 6), feat["source"], F(BC_SB, 5.2), MUTED, anchor="ra")
    hy, _ = draw_para(d, feat["head"], F(BC_B, 15.0), lx + 10, by + 18,
                      lw - 20, 15.5, INK, max_lines=2)
    if feat.get("deck"):
        hy, _ = draw_para(d, feat["deck"], F(SERIF, 8.6), lx + 10, hy + 2,
                          lw - 20, 10.4, INK, max_lines=3)

# ------------------------------------------------------------- compact card grid
GX0, GY0 = M, 436
gcols, ggap, gh = 5, 8, 136
gw = (CW - (gcols - 1) * ggap) // gcols
for k, feat in enumerate(FEATURED[3:13]):
    r, c = divmod(k, gcols)
    gx = GX0 + c * (gw + ggap)
    gy = GY0 + r * (gh + ggap)
    d.rectangle([gx, gy, gx + gw, gy + gh], outline=FAINT, width=1)
    feat["illus"](d, gx + 1, gy + 1, gw - 2, 76)
    tag(d, gx + 7, gy + 79, feat["tag"], fill=feat["tagc"], size=5.0)
    hy, _ = draw_para(d, feat["head"], F(BC_B, 9.6), gx + 7, gy + 91,
                      gw - 14, 11, INK, max_lines=3)
    text(d, (gx + 7, gy + gh - 11),
         f"{feat['n']:02d}  {fit(feat['source'], F(BC_SB, 5.0), gw - 22)}",
         F(BC_SB, 5.0), MUTED)

# ------------------------------------------------------------- section head
rule(d, M, 726, W - M, 726, 1, INK)
text(d, (M, 730), "WHERE IT HAPPENED", F(BC_B, 9.6), RED)
text(d, (W - M, 731), "ALSO ON FRIDAY 20 NOVEMBER — 24 MORE STORIES",
     F(BC_SB, 7.4), MUTED, anchor="ra")

# ------------------------------------------------------------- map
MX0, MY0, MX1, MY1 = M, 744, 340, 884
d.rectangle([MX0, MY0, MX1, MY1], fill=PETROL)
# stylised continents (kept inside the map frame, never over the masthead)
for pts in [
    [(58, 18), (96, 12), (118, 26), (108, 46), (86, 50), (80, 68), (58, 64), (46, 42)],
    [(118, 60), (142, 58), (148, 92), (130, 116), (118, 96)],
    [(150, 16), (240, 14), (268, 30), (250, 52), (214, 48), (196, 66), (170, 58), (156, 40)],
    [(206, 70), (240, 66), (252, 90), (230, 108), (214, 92)],
    [(270, 56), (312, 60), (318, 92), (288, 104), (270, 86)],
    [(270, 104), (296, 108), (294, 124), (276, 122)],
]:
    d.polygon([(MX0 + px, MY0 + py) for px, py in pts], fill=PETROL2)
pins = [(76, 34, 2), (132, 82, 6), (168, 38, 8), (196, 54, 3), (226, 30, 4),
        (244, 46, 13), (286, 74, 11), (296, 70, 5), (120, 44, 1), (224, 92, 7),
        (290, 116, 12), (158, 100, 9)]
for px, py, num in pins:
    ax, ay = MX0 + px, MY0 + py
    d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], fill=RED, outline=CREAM, width=1)
    text(d, (ax, ay), str(num), F(BC_B, 8), CREAM, anchor="mm")
text(d, (MX0 + 8, MY1 - 14), "RED PINS = DRAWN STORIES  ·  POSITIONS APPROXIMATE",
     F(BC_SB, 5.8), CREAM)

# ------------------------------------------------------------- briefs list
BX0 = 352
bcw = (W - M - BX0 - 10) / 2
for i, (head, src) in enumerate(BRIEFS):
    col = 0 if i < 12 else 1
    row = i if i < 12 else i - 12
    bx = BX0 + col * (bcw + 10)
    by = 746 + row * 11.2
    d.rectangle([bx, by + 2, bx + 2, by + 4], fill=RED)
    sf = F(SERIF, 7.9)
    srcw = F(BC_SB, 5.2).getlength(src)
    avail = bcw - 10 - srcw - 8
    text(d, (bx + 7, by - 1), fit(head, sf, avail), sf, INK)
    text(d, (bx + bcw, by), src, F(BC_SB, 5.2), MUTED, anchor="ra")

# ------------------------------------------------------------- date check
DC0 = 890
d.rectangle([M, DC0, W - M, DC0 + 54], fill=TINT)
d.rectangle([M, DC0, M + 4, DC0 + 54], fill=RED)
text(d, (M + 12, DC0 + 6), "DATE CHECK", F(BC_B, 8.6), RED)
text(d, (W - M - 10, DC0 + 7), "FRIDAY 20 NOVEMBER 2026", F(BC_SB, 6.8),
     MUTED, anchor="ra")
draw_para(d, DATE_CHECK, F(SERIF, 7.0), M + 12, DC0 + 19, CW - 24, 8.4, INK,
          max_lines=4)

# ------------------------------------------------------------- footer
rule(d, M, 950, W - M, 950, 1, INK)
draw_para(d, SOURCES, F(SERIF, 6.2), M, 954, 880, 7.4, MUTED, max_lines=2)
text(d, (W - M, 954), "PAGE 1 / 1", F(BC_SB, 6.6), MUTED, anchor="ra")

# ------------------------------------------------------------- audit
warn = 0
for box, s in AUDIT:
    x1, y1, x2, y2 = box
    if x1 < -1 or y1 < -1 or x2 > W + 1 or y2 > H + 1:
        print(f"WARN out of bounds: {s!r} {box}", file=sys.stderr)
        warn += 1
if warn:
    print(f"{warn} text warnings", file=sys.stderr)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "entry.png")
img.save(out, "PNG", optimize=True, compress_level=9)
print("saved", out, os.path.getsize(out), "bytes", img.size)
