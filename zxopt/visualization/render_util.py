import math
import re
from typing import Tuple

import cairo

BLACK = "#000000"

def color(ctx: cairo.Context, hex: str):
    m = re.match(r"#?([0-9A-Fa-f][0-9A-Fa-f])([0-9A-Fa-f][0-9A-Fa-f])([0-9A-Fa-f][0-9A-Fa-f])", hex)
    if not m:
        raise RuntimeError(f"Cannot parse color {hex}")
    ctx.set_source_rgb(int(m.group(1), 16) / 255.0, int(m.group(2), 16) / 255.0, int(m.group(3), 16) / 255.0)

def draw_line(ctx: cairo.Context, start: Tuple[float, float], end: Tuple[float, float], offset: Tuple[float, float] = (0, 0)):
    ctx.move_to(start[0] + offset[0], start[1] + offset[1])
    ctx.line_to(end[0] + offset[0], end[1] + offset[1])
    ctx.close_path()
    ctx.stroke()

def fill_circle(ctx: cairo.Context, pos: Tuple[float, float], radius: float):
    ctx.arc(pos[0], pos[1], radius, 0, 2*math.pi)
    ctx.fill()


# this is not really a baseline but rather a center
BASELINE_BOT = 0
BASELINE_CENTER = +0.5
BASELINE_TOP = +1.0

ALIGN_LEFT = 0
ALIGN_CENTER = -0.5
ALIGN_RIGHT = -1.0

def draw_text(ctx: cairo.Context, pos: Tuple[float, float], text: str, align: int = ALIGN_LEFT, baseline: int = BASELINE_BOT):
    (x, y, width, height, dx, dy) = ctx.text_extents(text)
    offset = (width * align, height * baseline)

    ctx.move_to(pos[0] + offset[0], pos[1] + offset[1])
    ctx.show_text(text)

def fill_square(ctx: cairo.Context, pos: Tuple[float, float], size: float):
    ctx.rectangle(pos[0] - size / 2.0, pos[1] - size / 2.0, size, size)
    ctx.fill()
