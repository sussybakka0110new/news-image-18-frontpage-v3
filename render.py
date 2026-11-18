"""Draw a LEGIBLE one-day world-news front page as a 1024x1024 PNG.

Standard library only: the PNG is assembled with struct and zlib, and all text
is painted from a hand-coded 5x7 bitmap font. Every headline is drawn at
scale 4 (20x28 px glyphs) so single characters survive being viewed at ~300px.
No network, no randomness: identical bytes on every run.
"""

import struct
import zlib

W = H = 1024

BG = (9, 14, 30)
PANEL = (16, 24, 46)
NAVY = (9, 14, 30)
GOLD = (232, 184, 59)
GOLD_DIM = (150, 112, 36)
CREAM = (245, 238, 215)
PALE = (196, 208, 230)
RED = (226, 78, 62)
LAND = (46, 66, 96)
COAST = (94, 124, 164)
RULE = (30, 43, 70)

DATE = "18 NOVEMBER 2026"

# 5x7 glyphs, one row per line. Uppercase only; only characters used here.
FONT = {
    "A": "01110/10001/10001/11111/10001/10001/10001",
    "B": "11110/10001/10001/11110/10001/10001/11110",
    "C": "01111/10000/10000/10000/10000/10000/01111",
    "D": "11110/10001/10001/10001/10001/10001/11110",
    "E": "11111/10000/10000/11110/10000/10000/11111",
    "F": "11111/10000/10000/11110/10000/10000/10000",
    "G": "01111/10000/10000/10111/10001/10001/01111",
    "H": "10001/10001/10001/11111/10001/10001/10001",
    "I": "11111/00100/00100/00100/00100/00100/11111",
    "J": "00111/00010/00010/00010/00010/10010/01100",
    "K": "10001/10010/10100/11000/10100/10010/10001",
    "L": "10000/10000/10000/10000/10000/10000/11111",
    "M": "10001/11011/10101/10101/10001/10001/10001",
    "N": "10001/11001/10101/10011/10001/10001/10001",
    "O": "01110/10001/10001/10001/10001/10001/01110",
    "P": "11110/10001/10001/11110/10000/10000/10000",
    "Q": "01110/10001/10001/10001/10101/10010/01101",
    "R": "11110/10001/10001/11110/10100/10010/10001",
    "S": "01111/10000/10000/01110/00001/00001/11110",
    "T": "11111/00100/00100/00100/00100/00100/00100",
    "U": "10001/10001/10001/10001/10001/10001/01110",
    "V": "10001/10001/10001/10001/10001/01010/00100",
    "W": "10001/10001/10001/10101/10101/11011/10001",
    "X": "10001/10001/01010/00100/01010/10001/10001",
    "Y": "10001/10001/01010/00100/00100/00100/00100",
    "Z": "11111/00001/00010/00100/01000/10000/11111",
    "0": "01110/10001/10011/10101/11001/10001/01110",
    "1": "00100/01100/00100/00100/00100/00100/01110",
    "2": "01110/10001/00001/00010/00100/01000/11111",
    "3": "11111/00010/00100/00010/00001/10001/01110",
    "4": "00010/00110/01010/10010/11111/00010/00010",
    "5": "11111/10000/11110/00001/00001/10001/01110",
    "6": "00110/01000/10000/11110/10001/10001/01110",
    "7": "11111/00001/00010/00100/01000/01000/01000",
    "8": "01110/10001/10001/01110/10001/10001/01110",
    "9": "01110/10001/10001/01111/00001/00010/01100",
    " ": "00000/00000/00000/00000/00000/00000/00000",
    ".": "00000/00000/00000/00000/00000/01100/01100",
    ",": "00000/00000/00000/00000/01100/01100/00110",
    "-": "00000/00000/00000/11111/00000/00000/00000",
    "/": "00001/00010/00010/00100/01000/01000/10000",
    ":": "00000/01100/01100/00000/01100/01100/00000",
    "&": "01100/10010/10100/01000/10101/10010/01101",
    "'": "00100/00100/00000/00000/00000/00000/00000",
    "?": "01110/10001/00001/00010/00100/00000/00100",
    "!": "00100/00100/00100/00100/00100/00000/00100",
    "|": "00100/00100/00100/00100/00100/00100/00100",
}

# 22 consequential, short, verified headlines: 11 per themed column.
# Each is wrapped at 19 chars, i.e. two lines at scale 4 -- never three.
SECTIONS = [
    ("WORLD / CONFLICT", [
        "KERCH BRIDGE PARTLY COLLAPSES",
        "ZELENSKY HAILS ATTACK",
        "KYIV DOUBLE-TAP KILLS 72",
        "RUSSIAN PLANE CRASH: 19 DEAD",
        "IRAN STRIKES BAHRAIN AGAIN",
        "TRUMP WARNED ON IRAN PLOT",
        "WEST BANK WOMAN, 72, SHOT",
        "EU STATES: RWANDA RETURN HUBS",
        "COSTA RICAN JOURNALIST SHOT",
        "ISOLATED BRAZIL TRIBE EMERGES",
        "US SOLDIER HELD IN UK",
    ]),
    ("POLITICS / TECH", [
        "NVIDIA REVENUE DOUBLES",
        "NVIDIA BOARD: NO HUANG RETURN",
        "TRUMP BACKS HUANG RETURN",
        "MEGASPEED CHIP EXPORT PROBE",
        "HUANG TO TESTIFY IN CONGRESS",
        "TRUMP, XI MEET AT APEC",
        "CHINA AI FACES NVIDIA SPY ROW",
        "XI, PUTIN START TALKS",
        "DEMOCRATS WIN ALASKA SEAT",
        "US LOSES MEASLES-FREE STATUS",
        "OIL SUPPLY BACK IN SURPLUS",
    ]),
]

COL_X = (20, 522)
COL_W = 482
WRAP_AT = 19
CARD_H = 64
LINE_STEP = 34  # 28 px of glyphs plus a 6 px dark gap: at ~300px view the gap is still one pixel, so two-line headlines never smear together

CANVAS = bytearray(BG * (W * H))


def rect(x, y, w, h, color):
    x0, y0 = max(0, x), max(0, y)
    x1, y1 = min(W, x + w), min(H, y + h)
    if x0 >= x1 or y0 >= y1:
        return
    row = bytes(color) * (x1 - x0)
    for yy in range(y0, y1):
        start = (yy * W + x0) * 3
        CANVAS[start:start + len(row)] = row


def outline(x, y, w, h, color, t=1):
    rect(x, y, w, t, color)
    rect(x, y + h - t, w, t, color)
    rect(x, y, t, h, color)
    rect(x + w - t, y, t, h, color)


def text_width(s, scale, gap=1):
    return (len(s) * (5 + gap) - gap) * scale if s else 0


def put_text(s, x, y, scale, color, gap=1):
    s = s.upper()
    for i, ch in enumerate(s):
        glyph = FONT.get(ch, FONT["?"])
        gx = x + i * (5 + gap) * scale
        for ry, rowstr in enumerate(glyph.split("/")):
            for rx, bit in enumerate(rowstr):
                if bit == "1":
                    rect(gx + rx * scale, y + ry * scale, scale, scale, color)


def put_centered(s, x0, x1, y, scale, color, gap=1):
    put_text(s, x0 + (x1 - x0 - text_width(s, scale, gap)) // 2, y, scale, color, gap)


def wrap(s, limit):
    words, lines, line = s.split(), [], ""
    for word in words:
        candidate = word if not line else line + " " + word
        if len(candidate) <= limit:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    if len(lines) > 2 or any(len(ln) > limit for ln in lines):
        raise ValueError("headline does not fit two lines: %r -> %r" % (s, lines))
    return lines


def marker(dot_x, dot_y, color, label, label_x, label_y):
    """Draw a marker and its label at explicit coordinates so labels never collide."""
    rect(dot_x - 2, dot_y - 2, 9, 9, NAVY)
    rect(dot_x, dot_y, 5, 5, color)
    put_text(label, label_x, label_y, 2, PALE)


def compose():
    # Gold masthead: small kicker and a very large date banner.
    rect(0, 0, W, 88, GOLD)
    rect(0, 84, W, 4, GOLD_DIM)
    put_centered("WORLD NEWS / THE DAILY FRONT PAGE", 0, W, 6, 2, NAVY)
    put_centered(DATE, 0, W, 26, 8, NAVY)

    # Two obvious section headers, drawn larger than any headline.
    for col, (label, stories) in enumerate(SECTIONS):
        x = COL_X[col]
        put_text(label, x + 4, 92, 4, GOLD)
        rect(x, 124, COL_W, 2, GOLD_DIM)

        for row, story in enumerate(stories):
            y = 132 + row * CARD_H
            rect(x, y + 62, COL_W, 1, RULE)
            rect(x + 1, y + 5, 5, 5, RED)
            lines = wrap(story, WRAP_AT)
            for line_no, line in enumerate(lines):
                put_text(line, x + 12, y + line_no * LINE_STEP, 4,
                         CREAM if line_no == 0 else PALE)

    # Simplified world map with ten flashpoint markers.
    rect(16, 842, 992, 142, PANEL)
    outline(16, 842, 992, 142, GOLD_DIM, 2)
    put_text("WORLD MAP / 10 FLASHPOINTS", 26, 848, 2, GOLD)
    put_centered("22 STORIES / 6 CONTINENTS", 700, 1004, 848, 2, GOLD)

    def land(x, y, w, h):
        rect(28 + x, 868 + y, w, h, LAND)
        outline(28 + x, 868 + y, w, h, COAST, 1)

    land(30, 6, 150, 36)     # North America
    land(65, 44, 48, 28)     # South America
    land(420, 8, 70, 22)     # Europe
    land(415, 36, 85, 44)    # Africa
    land(500, 4, 260, 36)    # Asia
    land(560, 40, 50, 20)    # South-east Asia
    land(740, 52, 80, 22)    # Oceania

    marker(105, 888, GOLD, "US", 84, 872)
    marker(120, 925, GOLD, "PERU", 90, 942)
    marker(470, 886, RED, "KYIV", 438, 858)
    marker(530, 884, GOLD, "RUSSIA", 526, 858)
    marker(560, 912, RED, "BAHRAIN", 580, 940)
    marker(450, 920, GOLD, "NIGERIA", 400, 944)
    marker(490, 936, RED, "RWANDA", 496, 924)
    marker(700, 890, GOLD, "BEIJING", 640, 912)
    marker(600, 920, GOLD, "MUMBAI", 668, 946)
    marker(800, 932, GOLD, "SYDNEY", 772, 946)

    put_centered("N.AMERICA  S.AMERICA  EUROPE  AFRICA  ASIA  OCEANIA",
                 16, 1008, 966, 2, GOLD_DIM)

    # Sourced footer.
    rect(0, 1000, W, 1, GOLD)
    put_centered("WORLD NEWS | " + DATE + " | SOURCES: BBC, GUARDIAN",
                 0, W, 1008, 2, GOLD)


def save_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw.extend(CANVAS[y * W * 3:(y + 1) * W * 3])

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)


if __name__ == "__main__":
    compose()
    save_png("entry.png")
