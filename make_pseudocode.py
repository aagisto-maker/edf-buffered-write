#!/usr/bin/env python3
"""Regenerate Fig_pseudocode.png at 300 DPI (side-by-side antipattern vs buffer-then-flush)."""
import sys, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

OUT = sys.argv[1] if len(sys.argv) > 1 else "."

left = [
    "open_writer(path, fs, n_ch)",
    "",
    "while acquiring:",
    "    block = device.read(b)      # b < fs",
    "    writer.writeSamples(block)  # -> full record!",
    "",
    "writer.close()",
]
right = [
    "open_writer(path, fs, n_ch)",
    "buffer = empty()",
    "while acquiring:",
    "    block = device.read(b)",
    "    buffer = concat(buffer, block)",
    "    while len(buffer) >= fs:    # one record",
    "        writer.writeSamples(buffer[:fs])",
    "        buffer = buffer[fs:]",
    "# flush remainder with LAST value, not zero",
    "if len(buffer) > 0:",
    "    pad = repeat(buffer[-1], fs - len(buffer))",
    "    writer.writeSamples(concat(buffer, pad))",
    "writer.close()",
]

FS = 10.5
DY = 0.066
fig = plt.figure(figsize=(10.6, 4.4))
fig.patch.set_facecolor("white")

def panel(ax, title, lines):
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.text(0.0, 1.05, title, fontsize=14, fontweight="bold",
            family="DejaVu Sans", va="bottom", ha="left")
    ax.add_patch(FancyBboxPatch((0.0, 0.0), 1.0, 1.0,
                 boxstyle="round,pad=0.004,rounding_size=0.012",
                 linewidth=1.0, edgecolor="0.5", facecolor="white",
                 transform=ax.transAxes, clip_on=False))
    y = 0.94
    for ln in lines:
        ax.text(0.03, y, ln, fontsize=FS, family="DejaVu Sans Mono",
                va="top", ha="left")
        y -= DY

axL = fig.add_axes([0.015, 0.05, 0.455, 0.82])
axR = fig.add_axes([0.525, 0.05, 0.470, 0.82])
panel(axL, "(a) Antipattern", left)
panel(axR, "(b) Buffer-then-flush", right)

out = os.path.join(OUT, "Fig_pseudocode.png")
fig.savefig(out, dpi=300, facecolor="white")
print("wrote", out)
