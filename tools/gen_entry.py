#!/usr/bin/env python3
"""Rebuild the Friday 20 November 2026 world-news front page.

Offline, deterministic, local fonts only. 1024x1024 PNG.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os
import sys

W = H = 1024
M = 36
CW = W - 2 * M

PAPER = (242, 238, 227)
INK = (20, 17, 13)
RED = (176, 30, 40)
NAVY = (23, 58, 68)
NAVY_2 = (32, 72, 82)
NAVY_3 = (48, 88, 96)
MUTED = (104, 96, 83)
FAINT = (191, 183, 169)
TINT = (232, 224, 210)
CREAM = (242, 238, 227)

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
        box = d.textbbox(xy, s, font=font, anchor=anchor)
        AUDIT.append((box, s))
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
        d.rectangle([x1, y1, x2, y2], fill=fill)
    else:
        d.line([x1, y1, x2, y2], fill=fill, width=width)


def wrap(s, font, maxw):
    words = s.split()
    lines = []
    cur = ""
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


# ---------------------------------------------------------------- content
# All 35 briefs are Friday 20 November 2026 items.  The lead is the day's
# biggest story.  Thursday 19 November items are named only in DATE CHECK.
COLUMNS = [
    ("WORLD & CLIMATE", [
        ("IMF warns world debt is nearing 100% of GDP",
         "Georgieva says public debt is at its highest share of global output since World War II.",
         "IMF"),
        ("IEA: data-centre emissions could rise 70%",
         "The agency warns emissions from data centres could climb about 70% by 2030.",
         "IEA"),
        ("COP31 enters its final day deadlocked",
         "Antalya talks stall on finance; Panama objects to a weak deal as overtime looms.",
         "GUARDIAN / REUTERS"),
        ("UN marks World Children’s Day",
         "The annual day highlights children’s rights and protection in conflict.",
         "UN"),
        ("BepiColombo reaches Mercury",
         "The ESA/JAXA probe arrives after an eight-year voyage; orbit insertion is next.",
         "ESA"),
        ("Early trial: pancreatic cancer pill shrinks tumours",
         "Researchers report responses in some patients; larger trials are still needed.",
         "REUTERS"),
        ("Tonga and Fiji declare drought emergencies",
         "Both Pacific governments act as El Niño-driven drought hits water and crops.",
         "RNZ / AP"),
    ]),
    ("EUROPE", [
        ("Kyiv hit by about 30 ballistic missiles",
         "Russian strikes hit energy and transport sites; embassies damaged and injuries reported.",
         "REUTERS / KYIV"),
        ("Tbilisi gas blast kills six, including a child",
         "An explosion collapses part of a residential block in Georgia’s capital.",
         "SCMP / AFP"),
        ("Italy’s CGIL holds 24-hour general strike",
         "Unions rally in 100 squares against the 2027 budget; transport faces disruption.",
         "CGIL / AFP"),
        ("Burnham opens first EU-UK reset summit",
         "The UK prime minister meets Costa and von der Leyen on agrifood and carbon links.",
         "EU COUNCIL"),
        ("Denmark backs Greenland defence bill",
         "Parliament approves a defence package for Greenland as Arctic tensions persist.",
         "AFP"),
        ("UK and Norway fund Ukraine’s navy",
         "London and Oslo commit more than £100m for two Ukrainian naval vessels.",
         "BBC"),
        ("France apartment fire kills one, injures 15",
         "A blaze in a residential building prompts a large emergency response.",
         "AP"),
    ]),
    ("ASIA & PACIFIC", [
        ("Japan October CPI holds at 2.3%",
         "Core inflation stays above the BoJ’s 2% target for a second month.",
         "REUTERS"),
        ("China holds lending rates for 18th month",
         "The one-year LPR stays at 3.0% and the five-year at 3.5%.",
         "REUTERS"),
        ("Asia shares slide in AI sell-off",
         "Tokyo and Seoul lead losses as chip stocks fall and AI valuations reset.",
         "REUTERS"),
        ("Korea court clears ex-PM Han Duck-soo",
         "The court overturns his conviction over the 2024 martial-law case.",
         "SBS"),
        ("Taiwan tightens short-selling curbs",
         "New measures take effect as authorities try to calm trading.",
         "REUTERS"),
        ("Indonesia passes asset-forfeiture bill",
         "Parliament approves a law letting courts seize assets from crime.",
         "REUTERS"),
        ("Hong Kong temple-fire suspect held",
         "A second suspect is remanded after a fire at a temple.",
         "AP"),
    ]),
    ("AFRICA & MIDDLE EAST", [
        ("Senegal migrant boat capsizes; four dead",
         "A boat overturns off Yenne; dozens are missing as rescuers search the Atlantic.",
         "AL JAZEERA"),
        ("South Africa spin to Test victory",
         "Simon Harmer bowls South Africa to a Test win.",
         "ICC"),
        ("Qatar U17: Austria beat South Africa 2-0",
         "Austria win their Under-17 World Cup match by two goals.",
         "FIFA"),
        ("Uganda landslide survivors take case to UN",
         "Survivors of a deadly landslide seek justice at the United Nations.",
         "AP"),
        ("Somalia airstrike kills 13 militants",
         "Officials say an airstrike killed 13 militants.",
         "AP"),
        ("Israel strikes Hezbollah missile site",
         "Israeli strikes hit a Hezbollah missile site in Lebanon.",
         "AP"),
        ("Tanker struck near Oman; fire reported",
         "A tanker is struck near Oman and catches fire.",
         "UKMTO / REUTERS"),
    ]),
    ("AMERICAS & OCEANIA", [
        ("Brazil: Lula meets Raoni on Indigenous land",
         "The president meets Chief Raoni as Indigenous territory is recognised.",
         "AL JAZEERA"),
        ("Mexico City marks Revolution Day",
         "A nationwide march marks the 1910 revolution.",
         "AP"),
        ("Haiti police kill 34 gang suspects",
         "Police kill 34 gang suspects in an operation, authorities say.",
         "AP"),
        ("El Salvador: Bukele registers for third term",
         "The president files for the 2027 vote; rights groups object.",
         "AP"),
        ("Fed minutes: most officials saw more tightening",
         "The minutes show most policymakers expected further rate rises.",
         "REUTERS"),
        ("AUKUS sub sales could shrink US fleet",
         "A US budget office warns the deal may reduce the US submarine fleet.",
         "REUTERS"),
        ("Bougainville: Rio Tinto pledges $70m",
         "The miner funds work on the legacy of the Panguna mine.",
         "REUTERS"),
    ]),
]


# ---------------------------------------------------------------- canvas
img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# folio
tracked(d, (M, 16), "THE GLOBAL WIRE", F(BC_B, 12.5), RED, 1.7)
text(d, (W - M, 17), "WORLD EDITION  ·  MORNING FINAL  ·  FRIDAY 20 NOVEMBER 2026",
     F(BC_M, 8.6), MUTED, anchor="ra")
rule(d, M, 34, W - M, 34, 1, INK)

# masthead: the date is the masthead
date_font = F(BC_BLACK, 92)
friday_w = date_font.getlength("FRIDAY")
text(d, (M, 46), "FRIDAY", date_font, RED)
text(d, (M + friday_w + 18, 46), "20 NOVEMBER 2026", date_font, INK)
text(d, (M, 150),
     "One day’s news, reported Friday 20 November 2026  ·  36 stories  ·  six continents",
     F(SERIF_IT, 13.4), INK)
text(d, (W - M, 151), "ORIGINAL DRAWINGS  ·  NO PHOTOGRAPHS",
     F(BC_SB, 7.2), MUTED, anchor="ra")
rule(d, M, 172, W - M, 172, 2, RED)

# contents strip
text(d, (M, 181), "36 STORIES", F(BC_B, 10.4), RED)
tracked(d, (M + 88, 182), "SIX CONTINENTS  ·  EVERY STORY FILED FRIDAY 20 NOVEMBER 2026",
        F(BC_SB, 8.2), INK, 1.0)
text(d, (W - M, 182), "LEAD + 35 BRIEFS", F(BC_SB, 8.2), MUTED, anchor="ra")
rule(d, M, 198, W - M, 198, 1, INK)

# ---------------------------------------------------------------- lead
tracked(d, (M, 209), "LEAD STORY  ·  BAY OF BENGAL", F(BC_B, 8.8), RED, 1.5)
head_font = F(BC_XB, 56)
text(d, (M, 221), "AKVAN MAKES LANDFALL NEAR GOPALPUR", head_font, INK)
deck_font = F(SERIF_SB, 16.2)
# Deck must stop before the locator map (mx=644), or "70–80 kmph" runs under it.
deck_w = 644 - M - 16
dy, dlines = draw_para(
    d,
    "Cyclone crosses the Odisha coast near Gopalpur; 3.72 lakh evacuated; winds 70–80 kmph, gusting 90.",
    deck_font, M, 284, deck_w, 18.4, INK, max_lines=2)
lead_body_y = dy + 2

body_font = F(SERIF, 10.4)
body_lh = 13.0
body_w = 288
col_a = (
    "Cyclone Akvan crossed the north Andhra Pradesh–south Odisha coast near Gopalpur on Friday "
    "morning, the IMD said, with landfall between about 7:30 and 8:30 am IST. Winds at crossing "
    "were 70–80 kmph, gusting 90, after the storm weakened from a severe cyclonic storm. After "
    "9:30 am it lay over south coastal Odisha, expected to weaken into a depression inland."
)
col_b = (
    "Odisha officials said about 3.72 lakh people had been evacuated to roughly 10,000 shelters. "
    "Heavy rain hit the coast: Patrapur 209 mm, Hinjili 207 mm and Gopalpur 190 mm in 24 hours to "
    "8:30 am. Schools were shut and many trains cancelled; 423 rescue teams were deployed. No major "
    "loss of life had been reported at the time of Friday midday reports."
)
draw_para(d, col_a, body_font, M, lead_body_y, body_w, body_lh, INK, justify=True, max_lines=8)
draw_para(d, col_b, body_font, M + body_w + 16, lead_body_y, body_w, body_lh, INK,
          justify=True, max_lines=8)

# lead numbers strip
num_top = 434
rule(d, M, num_top - 4, M + 600, num_top - 4, 1, INK)
cells = [
    ("3.72 LAKH", "people evacuated in Odisha", "house"),
    ("70–80", "kmph winds, gusting 90", "wind"),
    ("209 MM", "rain at Patrapur in 24h", "rain"),
    ("423", "rescue teams deployed", "ring"),
]
cell_w = 150
for i, (big, small, icon) in enumerate(cells):
    cx = M + i * cell_w
    ix, iy = cx, num_top + 3
    if icon == "house":
        d.polygon([(ix, iy + 7), (ix + 6, iy + 1), (ix + 12, iy + 7)], outline=RED)
        d.rectangle([ix + 2, iy + 7, ix + 10, iy + 13], outline=RED)
    elif icon == "wind":
        for k, yy in enumerate((iy + 3, iy + 7, iy + 11)):
            d.line([(ix, yy), (ix + 10 - k * 2, yy)], fill=RED, width=1)
            d.arc([ix + 7 - k * 2, yy - 3, ix + 13 - k * 2, yy + 3], 270, 90, fill=RED, width=1)
    elif icon == "rain":
        d.arc([ix + 1, iy + 1, ix + 11, iy + 10], 180, 360, fill=RED, width=1)
        d.line([(ix + 1, iy + 6), (ix + 11, iy + 6)], fill=RED, width=1)
        for k in range(3):
            d.line([(ix + 2 + k * 3, iy + 9), (ix + k * 3, iy + 13)], fill=RED, width=1)
    else:
        d.ellipse([ix + 1, iy + 1, ix + 11, iy + 11], outline=RED, width=1)
        d.ellipse([ix + 4, iy + 4, ix + 8, iy + 8], outline=RED, width=1)
        for ang in (0, 90, 180, 270):
            a = math.radians(ang)
            d.line([(ix + 6 + 3 * math.cos(a), iy + 6 + 3 * math.sin(a)),
                    (ix + 6 + 5 * math.cos(a), iy + 6 + 5 * math.sin(a))], fill=RED, width=1)
    text(d, (cx, num_top + 18), big, F(BC_XB, 23), INK)
    draw_para(d, small, F(SERIF, 7.3), cx, num_top + 43, cell_w - 8, 8.4, MUTED, max_lines=2)

# ---------------------------------------------------------------- locator map
mx, my, mw, mh = 644, 284, 344, 190
d.rectangle([mx, my, mx + mw, my + mh], fill=NAVY)
# sea texture
for yy in (my + 26, my + 48, my + 70):
    for k in range(5):
        x0 = mx + 196 + k * 28
        d.arc([x0, yy, x0 + 18, yy + 7], 200, 340, fill=NAVY_3, width=1)
# land
coast = [(150, 0), (145, 14), (138, 29), (130, 44), (122, 59), (115, 74),
         (108, 89), (100, 104), (92, 119), (84, 134), (76, 149), (68, 164),
         (60, 179), (55, 190)]
pts = [(mx + x, my + y) for x, y in coast]
land = [(mx, my), (mx + 150, my)] + pts + [(mx, my + mh)]
d.polygon(land, fill=(31, 60, 68))
d.line(pts, fill=CREAM, width=2, joint="curve")
# rain hatching over land
for i in range(5):
    for j in range(3):
        x0 = mx + 16 + i * 17
        y0 = my + 20 + j * 34
        d.line([(x0, y0), (x0 - 5, y0 + 9)], fill=(91, 123, 128), width=1)
# cyclone spiral
cx, cy = mx + 246, my + 118
spiral = []
for i in range(150):
    t = i / 149 * 2 * math.pi * 2.35
    r = 4 + 28 * (i / 149)
    spiral.append((cx + r * math.cos(t), cy + 0.72 * r * math.sin(t)))
d.line(spiral, fill=CREAM, width=1, joint="curve")
for rr, a0, a1 in ((42, 205, 335), (58, 205, 335), (74, 205, 335)):
    d.arc([cx - rr, cy - int(rr * 0.62), cx + rr, cy + int(rr * 0.62)],
          a0, a1, fill=NAVY_3, width=1)
d.ellipse([cx - 3, cy - 3, cx + 3, cy + 3], fill=RED)
# track
tx0, ty0 = mx + 330, my + 176
tx1, ty1 = mx + 112, my + 96
steps = 18
for i in range(steps):
    if i % 2 == 0:
        t0 = i / steps
        t1 = (i + 1) / steps
        p0 = (tx0 + (tx1 - tx0) * t0, ty0 + (ty1 - ty0) * t0)
        p1 = (tx0 + (tx1 - tx0) * t1, ty0 + (ty1 - ty0) * t1)
        d.line([p0, p1], fill=RED, width=2)
ang = math.atan2(ty1 - ty0, tx1 - tx0)
for s in (-0.55, 0.55):
    ex = tx1 - 10 * math.cos(ang + s)
    ey = ty1 - 10 * math.sin(ang + s)
    d.line([(tx1, ty1), (ex, ey)], fill=RED, width=2)
d.ellipse([tx1 - 7, ty1 - 7, tx1 + 7, ty1 + 7], outline=CREAM, width=1)
d.ellipse([tx1 - 4, ty1 - 4, tx1 + 4, ty1 + 4], fill=RED)
# labels
text(d, (mx + 14, my + 12), "INDIA", F(BC_B, 9), CREAM)
text(d, (mx + 28, my + 52), "ODISHA", F(BC_SB, 7), CREAM)
text(d, (mx + 10, my + 158), "ANDHRA PRADESH", F(BC_SB, 6.2), (185, 200, 199))
text(d, (mx + 248, my + 38), "BAY OF", F(BC_SB, 7.6), CREAM)
text(d, (mx + 248, my + 47), "BENGAL", F(BC_SB, 7.6), CREAM)
text(d, (mx + 200, my + 12), "CYCLONE AKVAN", F(BC_B, 7.4), RED)
text(d, (mx + 118, my + 84), "GOPALPUR", F(BC_B, 6.8), CREAM)
text(d, (mx + 132, my + 58), "PURI", F(BC_SB, 6.0), (185, 200, 199))
text(d, (mx + 60, my + 142), "NARSAPUR", F(BC_SB, 6.0), (185, 200, 199), anchor="ra")
text(d, (mx + 12, my + 174), "LANDFALL 07:30–08:30 IST", F(BC_SB, 6.2), CREAM)
text(d, (mx + mw - 10, my + 174), "IMD", F(BC_SB, 6.0), (185, 200, 199), anchor="ra")

# ---------------------------------------------------------------- briefs
brief_top = 540
tracked(d, (M, brief_top), "THE WORLD IN BRIEF", F(BC_B, 10.2), RED, 1.6)
text(d, (W - M, brief_top + 1), "35 stories  ·  reported Friday 20 November 2026",
     F(SERIF_IT, 7.6), MUTED, anchor="ra")
rule(d, M, brief_top + 14, W - M, brief_top + 14, 1, INK)

col_w = 180
col_gap = 13
col_x = [M + i * (col_w + col_gap) for i in range(5)]
head_font_b = F(BC_B, 11.4)
body_font_b = F(SERIF, 8.0)
source_font_b = F(BC_SB, 5.4)

header_y = brief_top + 22
for i, (label, items) in enumerate(COLUMNS):
    x = col_x[i]
    tracked(d, (x, header_y), label, F(BC_SB, 7.0), RED, 0.9)
    text(d, (x + col_w, header_y), str(len(items)), F(BC_SB, 6.6), MUTED, anchor="ra")
    rule(d, x, header_y + 11, x + col_w, header_y + 11, 1, FAINT)

row_y0 = brief_top + 38
row_h = 50


def draw_brief(d, x, y, w, head, body, source):
    hy, hlines = draw_para(d, head, head_font_b, x, y, w, 12.0, INK, max_lines=2)
    by, blines = draw_para(d, body, body_font_b, x, hy + 1, w, 9.0, INK, max_lines=2)
    sy = by + 1
    d.ellipse([x, sy + 2, x + 2, sy + 4], fill=RED)
    text(d, (x + 5, sy), source, source_font_b, MUTED)


for i, (label, items) in enumerate(COLUMNS):
    for j, (head, body, source) in enumerate(items):
        draw_brief(d, col_x[i], row_y0 + j * row_h, col_w, head, body, source)

# ---------------------------------------------------------------- date check
dc_top = 930
d.rectangle([M, dc_top, W - M, dc_top + 58], fill=TINT)
d.rectangle([M, dc_top, M + 4, dc_top + 58], fill=RED)
text(d, (M + 12, dc_top + 7), "DATE CHECK", F(BC_B, 8.6), RED)
text(d, (W - M - 10, dc_top + 8), "FRIDAY 20 NOVEMBER 2026", F(BC_SB, 6.8),
     MUTED, anchor="ra")
date_check = (
    "Excluded as Thursday 19 Nov news, not shown as Friday’s: the Trump–Xi–Putin Shenzhen summit "
    "and its four-point declaration; the ICJ Myanmar/Rohingya genocide judgment; the Houthi strike "
    "on Riyadh’s tallest tower; GTA VI’s launch-night sales records; Anthropic’s Nasdaq debut; the "
    "Van Gogh sale; the US Senate Iran war-powers vote; Trump’s Iran-strike delay."
)
draw_para(d, date_check, F(SERIF, 7.2), M + 12, dc_top + 20, CW - 24, 8.6, INK, max_lines=3)

# ---------------------------------------------------------------- footer
rule(d, M, 997, W - M, 997, 1, INK)
sources = (
    "Sources: IMD; The Statesman; India Today; Reuters; AP; AFP; BBC; The Guardian; SCMP; "
    "Al Jazeera; ICC; FIFA; ESA; UN; IMF; IEA; EU Council; RNZ; SBS; UKMTO. Bulletin times differ; "
    "COP31 was still in session when this edition closed."
)
draw_para(d, sources, F(SERIF, 6.2), M, 1002, 870, 7.2, MUTED, max_lines=2)
text(d, (W - M, 1002), "PAGE 1 / 1", F(BC_SB, 6.6), MUTED, anchor="ra")

# ---------------------------------------------------------------- audit
warn = 0
for box, s in AUDIT:
    x1, y1, x2, y2 = box
    if x1 < 0 or y1 < 0 or x2 > W or y2 > H:
        print(f"WARN out of bounds: {s!r} {box}", file=sys.stderr)
        warn += 1
if warn:
    print(f"{warn} text warnings", file=sys.stderr)

out = "/workspace/makefun/news-repo/entry.png"
img.save(out, "PNG", optimize=True, compress_level=9)
print("saved", out, os.path.getsize(out), "bytes", img.size)
