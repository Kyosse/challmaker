#!/usr/bin/env python3
"""
Encode a string as a layered-steps binary SVG (haikei style).

Each bit maps to one horizontal row :
  bit 1  →  step right edge at HIGH_X  (wide bar)
  bit 0  →  step right edge at LOW_X   (narrow bar)

Three colour layers are stacked (back → front), each slightly offset in x
to recreate the depth effect of the reference.
"""

from itertools import cycle
from random import randint

KEY = "PLOP"
TEXT = "interiut{SVGs_are_really_fun_and_powerfull}"
WIDTH = 1000
# ROW_H = WIDTH / (len(TEXT) * 8)
ROW_H = 10
HIGH_X = 720  # right edge when bit = 1
HIGH_X_2 = HIGH_X * 0.7
HIGH_X_3 = HIGH_X * 0.4

LOW_X = HIGH_X / 2  # right edge when bit = 0
LOW_X_2 = LOW_X * 0.7
LOW_X_3 = LOW_X * 0.4

BG = "#140021"

# layers: from back (darkest, smallest x) to front (brightest, full x) so it can be seen in the right order
LAYERS = [
    {"color": "#c77dff", "high": HIGH_X, "low": LOW_X},
    {"color": "#9900ff", "high": HIGH_X_2, "low": LOW_X_2},
    {"color": "#3700b6", "high": HIGH_X_3, "low": LOW_X_3},
]

OUTPUT = "flag.svg"

chars = list(TEXT)
bit_strs = [f"{ord(c):08b}" for c in chars]

key_bits = [int(b) for c in KEY for b in f"{ord(c):08b}"]
bits = [int(b) for bs in bit_strs for b in bs]
bits = [b ^ k for b, k in zip(bits, cycle(key_bits))]
n = len(bits)
HEIGHT = n * ROW_H


def make_path(bits, n, row_h, high_x, low_x, width, height):
    """
    Trace the right staircase edge of each row, then close
    by going to (0, height) and back up to (0, 0).

    Structure per row i  (y0 = i*row_h, y1 = (i+1)*row_h) :
        L{x[i]} {y0}   ← horizontal move to this row's right edge
        L{x[i]} {y1}   ← vertical drop to next row
    Open  : M{x[0]} 0
    Close : L0 {height}  L0 {y} for each y from height to 0  Z
    """
    xs = [high_x if b == 1 else low_x for b in bits]

    parts = [f"M{xs[0]} 0"]
    for i in range(n):
        y0 = i * row_h
        y1 = (i + 1) * row_h
        variation = 1 + (10**-2 * randint(-10, 10))
        parts.append(f"L{xs[i] * variation} {y0}")
        parts.append(f"L{xs[i] * variation} {y1}")

    # close: reach bottom-left then trace back up x=0
    parts.append(f"L0 {height}")
    for i in range(n, -1, -1):
        y = i * row_h
        parts.append(f"L0 {y}")
    parts.append("Z")

    return "".join(parts)


elements = []

# background
elements.append(f'<rect x="0" y="0" width="{WIDTH}" height="{HEIGHT}" fill="{BG}"/>')

for layer in LAYERS:
    d = make_path(bits, n, ROW_H, layer["high"], layer["low"], WIDTH, HEIGHT)
    elements.append(f'<path d="{d}" fill="{layer["color"]}"/>')

# HIGH / LOW reference dashed guides
elements.append(
    f'<line x1="{LOW_X}" y1="0" x2="{LOW_X}" y2="{HEIGHT}" '
    f'stroke="#440055" stroke-width="0.8" stroke-dasharray="4,6" opacity="0.4"/>'
)
elements.append(
    f'<line x1="{HIGH_X}" y1="0" x2="{HIGH_X}" y2="{HEIGHT}" '
    f'stroke="#220033" stroke-width="0.8" stroke-dasharray="4,6" opacity="0.3"/>'
)
elements.append(
    f'<text x="{LOW_X + 4}" y="9" font-family="monospace" font-size="8" '
    f'fill="#660088" opacity="0.7">0</text>'
)
elements.append(
    f'<text x="{HIGH_X + 4}" y="9" font-family="monospace" font-size="8" '
    f'fill="#440055" opacity="0.6">1</text>'
)

body = "\n  ".join(elements)
svg = (
    f'<?xml version="1.0" encoding="UTF-8"?>\n'
    f'<svg id="waveform" viewBox="0 0 {WIDTH} {HEIGHT}" '
    f'width="{WIDTH}" height="{HEIGHT}"\n'
    f'     xmlns="http://www.w3.org/2000/svg" version="1.1">\n'
    f"  {body}\n"
    f"</svg>\n"
)

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)

text = "".join(
    chr(int("".join(map(str, bits[i : i + 8])), 2))
    for i in range(0, len(bits), 8)
    if len(bits[i : i + 8]) == 8
)

print(f"[+] '{TEXT}'  →  {n} bits  →  {OUTPUT}  ({WIDTH}×{HEIGHT}px, row_h={ROW_H}px)")
for c, bs in zip(chars, bit_strs):
    print(f"    '{c}'  0x{ord(c):02X}  {bs}")
print(text.encode().hex())
