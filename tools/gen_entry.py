#!/usr/bin/env python3
"""Rebuild The Meridian's Friday 20 November 2026 world-news front page.

Offline, deterministic, local fonts only, 1024x1024 PNG.
Typographic-first: the date, six figures, three leads and five banners are
drawn large enough to survive a reduction to roughly 300 pixels across.
Illustrations are simple original diagrams, secondary to the type.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os
import sys

W = H = 1024
M = 30
CW = W - 2 * M

PAPER = (243, 238, 227)
INK = (20, 18, 16)
RED = (184, 40, 34)
RED_D = (142, 29, 25)
PETROL = (17, 48, 56)
PETROL2 = (27, 69, 77)
PETROL3 = (58, 100, 106)
MUTED = (103, 96, 84)
FAINT = (206, 199, 184)
TINT = (231, 223, 207)
AMBER = (213, 139, 48)
GREEN = (32, 92, 75)
WHITE = (250, 247, 239)

FONT_DIR = "/usr/share/fonts/truetype/sand-box"
DISPLAY = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-Black.ttf"
HEAD = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-ExtraBold.ttf"
HEADB = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-Bold.ttf"
SMALL = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-SemiBold.ttf"
MICRO = f"{FONT_DIR}/google/Barlow Condensed/BarlowCondensed-Medium.ttf"
SANS = f"{FONT_DIR}/custom/Source Sans Pro/SourceSansPro-Regular.ttf"
SERIF = f"{FONT_DIR}/custom/Source Serif Pro/SourceSerifPro-Regular.ttf"
SERIF_SB = f"{FONT_DIR}/custom/Source Serif Pro/SourceSerifPro-Semibold.ttf"
SERIF_IT = f"{FONT_DIR}/custom/Source Serif Pro/SourceSerifPro-It.ttf"

_fc = {}


def F(path, size):
    key = (path, round(size, 2))
    if key not in _fc:
        _fc[key] = ImageFont.truetype(path, int(round(size)))
    return _fc[key]


AUDIT = []


def text(d, xy, s, font, fill=INK, anchor="lt"):
    d.text(xy, s, font=font, fill=fill, anchor=anchor)
    try:
        AUDIT.append((d.textbbox(xy, s, font=font, anchor=anchor), s))
    except Exception:
        pass


def rule(d, x1, y1, x2, y2, width=1, fill=INK):
    if width <= 1:
        d.rectangle([int(x1), int(y1), int(x2), int(y2)], fill=fill)
    else:
        d.line([x1, y1, x2, y2], fill=fill, width=width)


def wrap(s, font, maxw):
    words, lines, cur = s.split(), [], ""
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
    cut = s
    while cut and font.getlength(cut + "\u2026") > maxw:
        cut = cut[:-1]
    return cut.rstrip(" ,.;:-") + "\u2026"


def para(d, s, font, x, y, maxw, lh, fill=INK, max_lines=None):
    lines = wrap(s, font, maxw)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1]
        while last and font.getlength(last + "\u2026") > maxw:
            last = last[:-1]
        lines[-1] = last.rstrip(" ,.;:") + "\u2026"
    for i, line in enumerate(lines):
        text(d, (x, y + i * lh), line, font, fill)
    return y + len(lines) * lh, lines


def tracked(d, xy, s, font, fill=INK, tracking=1.0):
    x, y = xy
    for ch in s:
        text(d, (x, y), ch, font, fill)
        x += font.getlength(ch) + tracking
    return x


def badge(d, x, y, n, r=9):
    d.ellipse([x - r, y - r, x + r, y + r], fill=RED)
    text(d, (x, y), str(n), F(HEADB, 10), WHITE, anchor="mm")


def tag(d, x, y, label, fill=RED, size=10.0):
    f = F(SMALL, size)
    wd = f.getlength(label) + 12
    d.rectangle([x, y, x + wd, y + 15], fill=fill)
    text(d, (x + 6, y + 2), label, f, WHITE)
    return wd


def banner_font(s, maxw, hi=25, lo=19):
    for sz in range(hi, lo - 1, -1):
        f = F(DISPLAY, sz)
        if f.getlength(s) <= maxw:
            return f
    return F(DISPLAY, lo)


# ---------------------------------------------------------- simple diagrams
def diag_kyiv(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for i in range(14):
        sx, sy = x + (i * 53) % w, y + (i * 31) % h
        d.ellipse([sx, sy, sx + 1, sy + 1], fill=PETROL3)
    ry = y + int(h * 0.60)
    d.rectangle([x, ry, x + w, ry + 16], fill=(22, 78, 90))
    d.line([x, ry, x + w, ry], fill=(150, 184, 172), width=1)
    for bx in (x + 52, x + 156, x + 260):
        deck = ry + 5
        d.line([bx - 38, deck, bx + 38, deck], fill=(198, 212, 206), width=4)
        for px in (bx - 26, bx + 26):
            d.line([px, deck, px, ry + 15], fill=(150, 174, 168), width=3)
        top = y + 9
        d.line([bx, top, bx, deck], fill=(198, 212, 206), width=3)
        for cx in (bx - 32, bx - 16, bx + 16, bx + 32):
            d.line([bx, top + 2, cx, deck], fill=(150, 174, 168), width=1)
    for j in range(3):
        sx = x + w - 18 - j * 24
        ex = x + 40 + j * 96
        d.line([sx, y + 4, ex, ry - 8], fill=RED, width=2)
        d.polygon([(ex, ry - 8), (ex - 6, ry - 16), (ex - 1, ry - 14)], fill=RED)
    ex, ey = x + 136, y + 26
    d.ellipse([ex - 10, ey - 10, ex + 10, ey + 10], fill=AMBER)
    for a in range(0, 360, 60):
        ra = math.radians(a)
        d.line([(ex + 12 * math.cos(ra), ey + 12 * math.sin(ra)),
                (ex + 17 * math.cos(ra), ey + 17 * math.sin(ra))], fill=RED, width=2)


def diag_akvan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for yy in range(y + 10, y + h - 4, 12):
        for k in range(8):
            sx = x + int(w * 0.46) + k * 32
            d.arc([sx, yy, sx + 22, yy + 8], 200, 340, fill=PETROL3)
    coast = [(x + int(w * .46), y), (x + int(w * .44), y + 20),
             (x + int(w * .40), y + 38), (x + int(w * .34), y + h)]
    d.polygon([(x, y)] + coast + [(x, y + h)], fill=(26, 78, 68))
    d.line(coast, fill=(150, 184, 172), width=2)
    cx, cy = x + int(w * .72), y + int(h * .46)
    for i in range(120):
        t = i / 119 * math.pi * 4.4
        r = 3 + 25 * i / 119
        d.point((cx + r * math.cos(t), cy + .68 * r * math.sin(t)), fill=WHITE)
    for rr in (40, 55):
        d.arc([cx - rr, cy - int(rr * .68), cx + rr, cy + int(rr * .68)],
              200, 340, fill=PETROL3, width=2)
    tx0, ty0 = x + w - 20, y + h - 22
    tx1, ty1 = x + int(w * .34), y + 38
    for i in range(0, 16, 2):
        p0 = (tx0 + (tx1 - tx0) * i / 16, ty0 + (ty1 - ty0) * i / 16)
        p1 = (tx0 + (tx1 - tx0) * (i + 1) / 16, ty0 + (ty1 - ty0) * (i + 1) / 16)
        d.line([p0, p1], fill=AMBER, width=2)
    d.ellipse([tx1 - 6, ty1 - 6, tx1 + 6, ty1 + 6], outline=WHITE, width=2)
    d.ellipse([tx1 - 3, ty1 - 3, tx1 + 3, ty1 + 3], fill=RED)
    text(d, (x + 8, y + 8), "GOPALPUR", F(SMALL, 9), WHITE)
    text(d, (x + w - 78, y + h - 16), "BAY OF BENGAL", F(MICRO, 8), (150, 184, 172))


def diag_markets(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    for gx in range(x + 16, x + w, 30):
        d.line([gx, y + 12, gx, y + h - 8], fill=PETROL2)
    for i, ht in enumerate((30, 25, 20)):
        bx = x + 40 + i * ((w - 88) / 3)
        d.rectangle([bx, y + h - 12 - ht, bx + 26, y + h - 12], fill=RED if i == 2 else (150, 60, 52))
    ax0, ay0 = x + w - 76, y + 22
    ax1, ay1 = x + 30, y + h - 20
    d.line([ax0, ay0, ax1, ay1], fill=AMBER, width=4)
    d.polygon([(ax1, ay1), (ax1 + 14, ay1 - 3), (ax1 + 3, ay1 - 15)], fill=AMBER)
    text(d, (x + 8, y + 6), "NIKKEI  KOSPI  TAIEX", F(MICRO, 8), (170, 190, 186))


def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=PETROL)
    shapes = [
        [(22, 24), (64, 16), (86, 32), (76, 56), (54, 60), (48, 84), (26, 78), (14, 50)],
        [(86, 74), (108, 72), (114, 114), (96, 134), (84, 108)],
        [(120, 20), (218, 16), (246, 34), (228, 60), (192, 56), (174, 76), (148, 68), (132, 46)],
        [(178, 86), (214, 82), (226, 112), (204, 130), (188, 110)],
        [(232, 68), (272, 72), (278, 108), (248, 120), (232, 100)],
    ]
    for pts in shapes:
        d.polygon([(x + px, y + py) for px, py in pts], fill=PETROL2)
    pins = [(40, 42, 1), (96, 100, 2), (150, 44, 3), (196, 62, 4),
            (250, 92, 5), (206, 108, 6), (120, 122, 7), (258, 78, 8)]
    for px, py, _ in pins:
        ax, ay = x + px, y + py
        d.ellipse([ax - 7, ay - 7, ax + 7, ay + 7], fill=RED, outline=WHITE, width=2)
        d.ellipse([ax - 2, ay - 2, ax + 2, ay + 2], fill=WHITE)
    text(d, (x + 10, y + 10), "WHERE IT HAPPENED", F(SMALL, 11), WHITE)
    text(d, (x + 10, y + h - 18), "PINS: KYIV \u00b7 ODISHA \u00b7 TOKYO \u00b7 ANTALYA", F(MICRO, 9), (176, 196, 190))
    text(d, (x + 10, y + h - 8), "TBILISI \u00b7 SENEGAL \u00b7 BRAZIL \u00b7 FIJI", F(MICRO, 9), (176, 196, 190))


# ------------------------------------------------------------------ content
STATS = [
    ("8", "killed across Ukraine", "REUTERS", RED),
    ("372,000", "evacuated in Odisha", "IMD", RED),
    ("\u22125.1%", "Nikkei 225, Friday", "REUTERS", INK),
    ("\u22126.2%", "Taiwan TAIEX", "REUTERS", INK),
    ("2.3%", "Japan October CPI", "REUTERS", INK),
    ("$120BN", "COP31 finance gap", "GUARDIAN", INK),
]

REGIONS = [
    ("EUROPE", 6, PETROL), ("ASIA", 7, RED), ("MID-EAST", 2, (158, 96, 42)),
    ("AFRICA", 3, GREEN), ("AMERICAS", 4, (120, 56, 74)),
    ("OCEANIA", 3, PETROL3), ("GLOBAL", 5, (90, 82, 66)),
]

LEADS = [
    dict(n=1, diagram=diag_kyiv, region="EUROPE", tag="KYIV \u00b7 WAR", tagc=RED,
         head="RUSSIAN MISSILE AND\nDRONE BARRAGE HITS KYIV",
         deck="Eight killed across Ukraine; Zelenskiy reported 400+ drones. Three Dnipro bridges and energy sites hit.",
         source="REUTERS"),
    dict(n=2, diagram=diag_akvan, region="ASIA", tag="ODISHA \u00b7 CYCLONE", tagc=RED,
         head="CYCLONE AKVAN CROSSES\nINDIA'S EAST COAST",
         deck="Landfall near Gopalpur, 7:30\u20138:30 am IST; winds 70\u201380 kmph, gusting 90. 372,000 evacuated in Odisha; no major death toll at midday.",
         source="IMD / STATESMAN / INDIA TODAY"),
    dict(n=3, diagram=diag_markets, region="ASIA", tag="TOKYO \u00b7 MARKETS", tagc=RED,
         head="AI SELL-OFF SLAMS\nASIAN SHARE MARKETS",
         deck="Nikkei 225 \u22125.1%, Kospi \u22125.2%, Taiwan TAIEX \u22126.2% as chip and AI valuations reset on Friday.",
         source="REUTERS"),
]

BANNERS = [
    dict(banner="COP31: DEADLOCK", fill=GREEN,
         head="Antalya's final day stalls; draft drops fossil-fuel text, $120bn finance gap open.",
         source="GUARDIAN / REUTERS", region="MID-EAST"),
    dict(banner="DEBT NEARS 100%", fill=RED,
         head="IMF's Georgieva: global public debt closing in on 100% of world GDP.",
         source="IMF", region="GLOBAL"),
    dict(banner="DATA CENTRES +70%", fill=PETROL,
         head="IEA warns datacentre emissions could rise about 70% by 2030.",
         source="IEA", region="GLOBAL"),
    dict(banner="TBILISI: 6 DEAD", fill=RED_D,
         head="Gas blast in the Georgian capital kills six, officials say.",
         source="SCMP / AFP", region="EUROPE"),
    dict(banner="EU\u2013UK RESET", fill=PETROL2,
         head="Burnham opens the first EU\u2013UK reset summit; no deal announced.",
         source="EU COUNCIL / AFP", region="EUROPE"),
]

MORE = [
    ("Japan CPI holds at 2.3%", "REUTERS", "ASIA"),
    ("China holds LPR at 3.0%", "REUTERS", "ASIA"),
    ("BepiColombo at Mercury", "ESA", "GLOBAL"),
    ("CGIL strike hits Italy", "CGIL / AFP", "EUROPE"),
    ("Senegal migrant boat", "AL JAZEERA", "AFRICA"),
    ("Lula meets Raoni", "AL JAZEERA", "AMERICAS"),
    ("Panguna mine pledge", "REUTERS", "OCEANIA"),
    ("Bukele seeks term three", "AP", "AMERICAS"),
    ("Kenya oil well strikes", "REUTERS", "AFRICA"),
    ("UN marks Children's Day", "UN", "GLOBAL"),
    ("UK, Norway fund Kyiv", "BBC", "EUROPE"),
    ("Seoul court clears ex-PM", "SBS", "ASIA"),
    ("Taiwan curbs shorts", "REUTERS", "ASIA"),
    ("Indonesia forfeiture bill", "REUTERS", "ASIA"),
    ("Israel strikes Hezbollah", "AP", "MID-EAST"),
    ("Mexico Revolution Day", "AP", "AMERICAS"),
    ("Tonga, Fiji drought", "RNZ / AP", "OCEANIA"),
    ("Pancreatic pill trial", "REUTERS", "GLOBAL"),
    ("Fed minutes: tightening", "REUTERS", "AMERICAS"),
    ("Denmark backs Greenland bill", "AFP", "EUROPE"),
    ("South Africa wins Test", "ICC", "AFRICA"),
    ("Phillips 118 v India", "ICC", "OCEANIA"),
    ("Gold, silver slump 4%+", "CNBC-TV18", "ASIA"),
    ("UN succession talks stall", "REUTERS", "GLOBAL"),
]

DATE_CHECK = (
    "EXCLUDED AS THURSDAY 19 NOVEMBER NEWS, NOT SOLD AS FRIDAY'S: the Trump\u2013Xi\u2013Putin Shenzhen "
    "summit and its four-point declaration; the ICJ Myanmar/Rohingya judgment; the Houthi strike on "
    "Riyadh's tallest tower; GTA VI launch-night sales; Anthropic's Nasdaq debut; the Van Gogh sale; "
    "the US Senate Iran war-powers vote; and Trump's Iran-strike delay."
)

SOURCES = (
    "Sources on each story. IMD; The Statesman; India Today; Reuters; AP; AFP; BBC; The Guardian; "
    "SCMP; Al Jazeera; ICC; ESA; UN; IMF; IEA; EU Council; RNZ; SBS. "
    "Times and bulletins differ; COP31 was still in session at Friday's close. Figures are as first reported."
)

# ------------------------------------------------------------------- canvas
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# folio
tracked(d, (M, 12), "THE MERIDIAN", F(HEADB, 14), RED, 1.8)
text(d, (W - M, 14), "WORLD EDITION  \u00b7  MORNING FINAL  \u00b7  NO. 326",
     F(MICRO, 11), MUTED, anchor="rt")
rule(d, M, 32, W - M, 32, 1, INK)

# masthead ribbon
d.rectangle([M, 38, W - M, 54], fill=RED)
text(d, (M + 8, 41), "ONE DAY  \u00b7  ONE PAGE  \u00b7  SIX CONTINENTS  \u00b7  ORIGINAL DRAWINGS",
     F(SMALL, 11), WHITE)
text(d, (W - M - 8, 41), "FRIDAY 20 NOVEMBER 2026", F(SMALL, 11), WHITE, anchor="rt")

# huge date headline
date_font = F(DISPLAY, 90)
fw = date_font.getlength("FRIDAY ")
text(d, (M, 60), "FRIDAY", date_font, RED)
text(d, (M + fw + 10, 60), "20 NOVEMBER 2026", date_font, INK)

# one-line deck
text(d, (M, 156),
     "Russia's barrage kills eight in Ukraine \u00b7 Cyclone Akvan ashore in India \u00b7 Asian markets slide \u00b7 COP31 ends deadlocked",
     F(SERIF, 18), INK)
rule(d, M, 184, W - M, 184, 2, RED)

# six stat chips
cell = CW / 6
for i, (big, lab, src, col) in enumerate(STATS):
    cx = M + i * cell
    if i:
        rule(d, cx - 5, 192, cx - 5, 254, 1, FAINT)
    text(d, (cx + 4, 190), big, F(HEAD, 36), col)
    text(d, (cx + 4, 232), lab, F(SANS, 13), INK)
    text(d, (cx + 4, 248), src, F(MICRO, 10), MUTED)
rule(d, M, 258, W - M, 258, 1, INK)

# thin region-count bar
story_regions = [f["region"] for f in LEADS + BANNERS] + [r for _, _, r in MORE]
bar = [(label, story_regions.count(label), col) for label, _, col in REGIONS]
total = sum(n for _, n, _ in bar)
rx = M
for label, n, col in bar:
    rw = CW * n / total
    d.rectangle([rx, 263, rx + rw - 2, 280], fill=col)
    lab = f"{label} {n}"
    f = F(SMALL, 10)
    if f.getlength(lab) <= rw - 10:
        text(d, (rx + 6, 265), lab, f, WHITE)
    else:
        text(d, (rx + 6, 265), label, F(MICRO, 9), WHITE)
    rx += rw

# three leads
text(d, (M, 287), "THE DAY'S THREE LEADS", F(HEADB, 12), RED)
text(d, (W - M, 288), f"{len(LEADS) + len(BANNERS) + len(MORE)} STORIES \u00b7 {len(REGIONS)} REGIONS \u00b7 ORIGINAL DIAGRAMS", F(SMALL, 11), MUTED, anchor="rt")

lgap = 12
lw = (CW - 2 * lgap) / 3
for i, feat in enumerate(LEADS):
    lx = M + i * (lw + lgap)
    d.rectangle([lx, 306, lx + lw, 500], outline=FAINT, width=1)
    feat["diagram"](d, int(lx) + 1, 307, int(lw) - 2, 60)
    tw = tag(d, int(lx) + 8, 371, feat["tag"], fill=feat["tagc"], size=10)
    text(d, (lx + lw - 8, 373), feat["source"], F(MICRO, 9), MUTED, anchor="rt")
    for j, line in enumerate(feat["head"].split("\n")):
        text(d, (lx + 8, 390 + j * 31), line, F(HEADB, 30), INK)
    para(d, feat["deck"], F(SANS, 13), lx + 8, 456, lw - 16, 15, INK, max_lines=3)

# five banner cards
text(d, (M, 508), "FIVE MORE FRONT-PAGE STORIES", F(HEADB, 12), RED)
bgap = 8
bw = (CW - 4 * bgap) / 5
for i, card in enumerate(BANNERS):
    bx = M + i * (bw + bgap)
    d.rectangle([bx, 527, bx + bw, 642], outline=FAINT, width=1)
    d.rectangle([bx + 1, 528, bx + bw - 1, 561], fill=card["fill"])
    bf = banner_font(card["banner"], bw - 14)
    text(d, (bx + 7, 534), card["banner"], bf, WHITE)
    para(d, card["head"], F(SANS, 13), bx + 7, 567, bw - 14, 15, INK, max_lines=3)
    text(d, (bx + 7, 626), card["source"], F(MICRO, 9), MUTED)

# where it happened / also on Friday
rule(d, M, 652, W - M, 652, 1, INK)
text(d, (M, 657), "WHERE IT HAPPENED", F(HEADB, 12), RED)
text(d, (W - M, 658), f"ALSO ON FRIDAY 20 NOVEMBER \u2014 {len(MORE)} MORE STORIES", F(SMALL, 11), MUTED, anchor="rt")

draw_map(d, M, 676, 268, 188)

lx0 = M + 282
listw = (W - M - lx0 - 2 * 12) / 3
for i, (head, src, _) in enumerate(MORE):
    col, row = divmod(i, 8)
    bx = lx0 + col * (listw + 12)
    by = 678 + row * 23
    text(d, (bx, by), f"{i+1:02d}", F(HEADB, 15), RED)
    sf = F(MICRO, 10)
    sw = sf.getlength(src) + 6
    text(d, (bx + listw, by + 3), src, sf, MUTED, anchor="rt")
    text(d, (bx + 27, by), fit(head, F(SMALL, 16), listw - 29 - sw), F(SMALL, 16), INK)

# date check
d.rectangle([M, 876, W - M, 958], fill=TINT)
d.rectangle([M, 876, M + 5, 958], fill=RED)
text(d, (M + 14, 882), "DATE CHECK \u2014 LEFT OUT: THURSDAY 19 NOVEMBER", F(HEADB, 15), RED)
text(d, (W - M - 10, 884), "NOT FRIDAY'S NEWS", F(SMALL, 11), MUTED, anchor="rt")
para(d, DATE_CHECK, F(SANS, 13), M + 14, 903, CW - 28, 15, INK, max_lines=4)

# footer
rule(d, M, 968, W - M, 968, 1, INK)
para(d, SOURCES, F(SANS, 12), M, 973, CW - 110, 14, MUTED, max_lines=2)
text(d, (W - M, 974), "PAGE 1 / 1", F(SMALL, 10), MUTED, anchor="rt")

# out-of-bounds audit
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

prev_dir = "/tmp/news-top30"
os.makedirs(prev_dir, exist_ok=True)
small = img.resize((300, 300), Image.LANCZOS)
small.save(os.path.join(prev_dir, "entry-300.png"), "PNG")
small.resize((600, 600), Image.NEAREST).save(os.path.join(prev_dir, "entry-300-x2.png"), "PNG")
