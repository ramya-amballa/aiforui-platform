"""Deterministic frame drawing (Pillow). No LLM involved anywhere here --
every pixel comes from the template's own configured fonts/colors/positions
plus the question's own text. See src/video/renderer.py for how frames are
sequenced into a video with ffmpeg.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from src.models import VALID_OPTION_KEYS, NormalizedQuestion
from src.video.fonts import load_font


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list:
    words = text.split()
    lines, current = [], ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if draw.textlength(candidate, font=font) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _draw_wrapped(draw, text, font, xy, max_width, fill, line_spacing):
    x, y = xy
    lines = _wrap_text(draw, text, font, max_width)
    line_height = font.size + line_spacing
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += line_height
    return y


def render_question_frame(tpl: dict, resolution: tuple, q: NormalizedQuestion,
                           highlight_key: str | None = None, timer_text: str | None = None,
                           show_banner: bool = False) -> Image.Image:
    """One frame: question + four options, optionally with the correct
    option highlighted, a countdown number, and/or an "answer revealed"
    banner. This single function renders every visual state the spec's
    question -> options -> countdown -> reveal sequence needs.
    """
    w, h = resolution
    bg_color = tpl["background"]["color"]
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    qf = tpl["fonts"]["question"]
    q_font = load_font(qf["family"], qf["size"])
    qx, qy = tpl["layout"]["question"]["position"]
    _draw_wrapped(
        draw, q.question, q_font, (qx, qy),
        tpl["layout"]["question"]["max_width"], qf["color"],
        tpl["layout"]["question"].get("line_spacing", 10),
    )

    opt_layout = tpl["layout"]["options"]
    ox, oy = opt_layout["start_position"]
    box_w = opt_layout["box_width"]
    box_h = opt_layout["box_height"]
    gap = opt_layout["row_gap"]
    pad = opt_layout["text_padding"]

    label_font = load_font(tpl["fonts"]["option_label"]["family"], tpl["fonts"]["option_label"]["size"])
    text_font = load_font(tpl["fonts"]["option_text"]["family"], tpl["fonts"]["option_text"]["size"])
    colors = tpl["colors"]

    banner_font = load_font(tpl["fonts"]["banner"]["family"], tpl["fonts"]["banner"]["size"])
    banner_color = tpl["fonts"]["banner"]["color"]

    for i, key in enumerate(VALID_OPTION_KEYS):
        top = oy + i * (box_h + gap)
        is_correct = highlight_key == key
        box_fill = colors["correct_box"] if is_correct else colors["option_box"]
        box_border = colors["correct_box_border"] if is_correct else colors["option_box_border"]
        draw.rounded_rectangle(
            [(ox, top), (ox + box_w, top + box_h)], radius=14, fill=box_fill, outline=box_border, width=3
        )
        label_color = colors["correct_box_border"] if is_correct else tpl["fonts"]["option_label"]["color"]
        draw.text((ox + pad, top + box_h / 2), f"{key}", font=label_font, fill=label_color, anchor="lm")
        label_w = draw.textlength(f"{key}.  ", font=label_font)
        draw.text(
            (ox + pad + label_w, top + box_h / 2), q.options[key], font=text_font,
            fill=tpl["fonts"]["option_text"]["color"], anchor="lm",
        )
        # The correctness indicator sits beside its own option box rather
        # than as a separate overlay, so it can never collide with the
        # question text or another option regardless of question length.
        if is_correct and show_banner:
            draw.text((ox + box_w - pad, top + box_h / 2), "✓ CORRECT",
                      font=banner_font, fill=banner_color, anchor="rm")

    if timer_text:
        tf = tpl["fonts"]["timer"]
        timer_font = load_font(tf["family"], tf["size"])
        tx, ty = tpl["layout"]["timer"]["position"]
        radius = int(tf["size"] * 0.75)
        draw.ellipse([(tx - radius, ty - radius), (tx + radius, ty + radius)], outline=tf["color"], width=6)
        draw.text((tx, ty), timer_text, font=timer_font, fill=tf["color"], anchor="mm")

    footer_cfg = tpl["layout"].get("footer")
    if footer_cfg:
        ff = tpl["fonts"]["footer"]
        footer_font = load_font(ff["family"], ff["size"])
        fx, fy = footer_cfg["position"]
        draw.text((fx, fy), footer_cfg.get("text", ""), font=footer_font, fill=ff["color"])

    return img
