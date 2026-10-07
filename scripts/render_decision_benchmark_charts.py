"""Render static README charts from aggregate metrics only (requires Pillow)."""
from __future__ import annotations

import json
import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "docs/assets"
LOCAL, API, INK, MUTED, GRID = "#147d92", "#b85b21", "#172536", "#536579", "#e0e7ee"


def font(size):
    for name in ("C:/Windows/Fonts/segoeui.ttf", "DejaVuSans.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            pass
    raise RuntimeError("A scalable Segoe UI or DejaVu Sans font is required")


def label(draw, xy, text, size=23, color=INK, anchor="la"):
    draw.text(xy, text, fill=color, font=font(size), anchor=anchor)


def mark(draw, x, y, remote=False):
    color = API if remote else LOCAL
    if remote:
        draw.polygon([(x, y - 8), (x + 8, y), (x, y + 8), (x - 8, y)], fill=color)
    else:
        draw.ellipse((x - 7, y - 7, x + 7, y + 7), fill=color)


def performance(rows):
    image = Image.new("RGB", (1600, 1050), "white")
    draw = ImageDraw.Draw(image)
    label(draw, (36, 30), "Choice benchmark | 150 matched public cases", 36)
    label(draw, (36, 86), "MASSIVE ja/en/zh + XNLI en/zh | RTX 5060 Ti 16GB | 2026-10-07", 23, MUTED)
    mark(draw, 46, 146)
    label(draw, (64, 130), "Local: after warmup", 22)
    mark(draw, 378, 146, True)
    label(draw, (396, 130), "API: network included", 22)
    label(draw, (555, 180), "Source-label accuracy (%)", 26)
    label(draw, (1090, 180), "Response time (ms, log scale)", 26)
    start, gap = 251, 47
    bottom = start + (len(rows) - 1) * gap + 30
    for tick in (0, 25, 50, 75, 100):
        x = 560 + tick * 3.7
        draw.line((x, 224, x, bottom), fill=GRID, width=2)
        label(draw, (x, bottom + 12), str(tick), 22, MUTED, "ma")
    def latency_x(value):
        return 1090 + (math.log10(value) - 1) / (math.log10(20000) - 1) * 330
    for tick in (10, 100, 1000, 10000):
        x = latency_x(tick)
        draw.line((x, 224, x, bottom), fill=GRID, width=2)
        label(draw, (x, bottom + 12), f"{tick:,}", 22, MUTED, "ma")
    for index, row in enumerate(rows):
        y = start + gap * index
        remote = row["kind"] == "api"
        color = API if remote else LOCAL
        label(draw, (36, y - 16), row["label"], 23)
        end = 560 + row["accuracy_pct"] * 3.7
        draw.rounded_rectangle((560, y - 8, end, y + 8), radius=3, fill=color)
        label(draw, (1035, y - 16), f"{row['accuracy_pct']:.2f}%", 23, INK, "ra")
        low, high, mean = map(latency_x, (row["min_ms"], row["max_ms"], row["mean_ms"]))
        draw.line((low, y, high, y), fill=color, width=3)
        for x in (low, high):
            draw.line((x, y - 5, x, y + 5), fill=color, width=2)
        mark(draw, mean, y, remote)
        label(draw, (1560, y - 16), f"{row['mean_ms']:,.1f}", 23, INK, "ra")
    label(draw, (36, 952), "Time: marker = mean; line = observed min-max (not a confidence interval).", 23, MUTED)
    label(draw, (36, 990), "Local: batch 1, 8 warmups. CPU-offload configurations include weight transfers; API server hardware is unknown.", 22, MUTED)
    image.save(ASSETS / "decision-engine-performance.png")


def resources(rows):
    rows = [row for row in rows if row["kind"] == "local"]
    image = Image.new("RGB", (1600, 820), "white")
    draw = ImageDraw.Draw(image)
    label(draw, (36, 28), "Initialization and memory | local configurations", 36)
    label(draw, (36, 84), "Cached weights; download and Python startup excluded | API server initialization/memory: unknown", 23, MUTED)
    columns = [("init_seconds", "Initialization (s)", 570, 235, 100, (0, 25, 50, 75, 100)),
               ("peak_rss_gib", "Process RAM peak (GiB)", 915, 220, 50, (0, 10, 20, 30, 40, 50)),
               ("gpu_increment_gib", "VRAM increment (GiB)", 1270, 205, 16, (0, 4, 8, 12, 16))]
    start, gap, bottom = 219, 45, 659
    for key, title, left, width, maximum, ticks in columns:
        label(draw, (left, 142), title, 25)
        for tick in ticks:
            x = left + tick / maximum * width
            draw.line((x, 182, x, bottom), fill=GRID, width=2)
            label(draw, (x, bottom + 12), str(tick), 22, MUTED, "ma")
        for index, row in enumerate(rows):
            y = start + index * gap
            value = row[key]
            if value is None:
                label(draw, (left + width + 65, y - 16), "Unused", 21, MUTED, "ra")
                continue
            mark(draw, left + value / maximum * width, y)
            label(draw, (left + width + 75, y - 16), f"{value:.2f}", 22, INK, "ra")
    for index, row in enumerate(rows):
        label(draw, (36, start + index * gap - 16), row["label"], 23)
    label(draw, (36, 739), "VRAM = sampled whole-GPU peak minus baseline; not isolated model memory. RAM = process peak RSS.", 22, MUTED)
    label(draw, (36, 777), "CLEF offload uses CPU RAM and GPU transfers. Initializations are single observations; filesystem cache is not reset.", 22, MUTED)
    image.save(ASSETS / "decision-engine-resources.png")


def main():
    data = json.loads((ASSETS / "decision-engine-benchmark.json").read_text(encoding="utf-8"))
    rows = data["rows"]
    if len(rows) != 14 or any(row["n"] != 150 for row in rows):
        raise ValueError("Expected the matched 150-case, 14-configuration aggregate")
    performance(rows)
    resources(rows)
    print("Rendered two static charts from aggregate metrics; no datasets or API access.")


if __name__ == "__main__":
    main()
