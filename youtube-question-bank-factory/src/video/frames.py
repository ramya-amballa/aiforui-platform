"""Deterministic frame drawing (Pillow). No LLM involved anywhere here --
every pixel comes from the template's own configured fonts/colors/positions
plus the question's own text. See src/video/renderer.py for how frames are
sequenced into a video with ffmpeg.
"""
from __future__ import annotations

from PIL import Image, ImageDraw

from src.models import VALID_OPTION_KEYS, NormalizedQuestion
from src.video.fonts import load_font

# A still-clearly-readable floor for the question font -- pagination
# kicks in only when even this floor can't fit the question on one page
# above the options box. Never used as a starting point for further
# shrinking; this is the smallest the question font is ever allowed to be.
_QUESTION_FONT_FLOOR_FRACTION = 0.85
_QUESTION_TEXT_BOTTOM_MARGIN = 24  # keeps a paginated/long question clearly separated from the options box


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
                           show_banner: bool = False, question_text_override: str | None = None,
                           question_font_size: int | None = None, show_options: bool = True) -> Image.Image:
    """One frame: question + four options, optionally with the correct
    option highlighted, a countdown number, and/or an "answer revealed"
    banner. This single function renders every visual state the spec's
    question -> options -> countdown -> reveal sequence needs.

    question_text_override/question_font_size/show_options exist only for
    long-question pagination (see plan_question_pages): a continuation
    page passes the page's own text slice, the floor font size, and
    show_options=False so it doesn't compete with the (not-yet-relevant)
    options for space. Every existing call site that doesn't pass them
    behaves exactly as before -- this is the single question-fits-fine
    frame the whole question+options sequence already used.
    """
    w, h = resolution
    bg_color = tpl["background"]["color"]
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    qf = tpl["fonts"]["question"]
    q_font = load_font(qf["family"], question_font_size or qf["size"])
    qx, qy = tpl["layout"]["question"]["position"]
    question_text = question_text_override if question_text_override is not None else q.question
    _draw_wrapped(
        draw, question_text, q_font, (qx, qy),
        tpl["layout"]["question"]["max_width"], qf["color"],
        tpl["layout"]["question"].get("line_spacing", 10),
    )

    if show_options:
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
            # The correctness indicator sits beside its own option box
            # rather than as a separate overlay, so it can never collide
            # with the question text or another option regardless of
            # question length.
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


def plan_question_pages(tpl: dict, question_text: str) -> tuple:
    """Decides how a question's text should be rendered above the options
    box, in priority order:
      1. at the template's own base question font size, if it fits on one
         page -- the common case, byte-identical to the pre-pagination
         behavior;
      2. else at a mildly reduced but still clearly readable size
         (_QUESTION_FONT_FLOOR_FRACTION of base), if that alone makes it
         fit on one page;
      3. else split across multiple pages at that same floor size --
         never smaller, and the question is never truncated, reworded, or
         had words dropped: each page is an exact, whitespace-joined
         slice of question_text.

    Returns (pages, font_size). len(pages) == 1 covers both cases 1 and 2.
    """
    img = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(img)

    qf = tpl["fonts"]["question"]
    base_size = qf["size"]
    max_width = tpl["layout"]["question"]["max_width"]
    line_spacing = tpl["layout"]["question"].get("line_spacing", 10)
    qy = tpl["layout"]["question"]["position"][1]
    options_y = tpl["layout"]["options"]["start_position"][1]
    available_height = max(options_y - qy - _QUESTION_TEXT_BOTTOM_MARGIN, base_size + line_spacing)

    floor_size = max(int(base_size * _QUESTION_FONT_FLOOR_FRACTION), 1)
    for size in (base_size, floor_size):
        font = load_font(qf["family"], size)
        max_lines = max(1, int(available_height // (font.size + line_spacing)))
        if len(_wrap_text(draw, question_text, font, max_width)) <= max_lines:
            return [question_text], size

    font = load_font(qf["family"], floor_size)
    max_lines = max(1, int(available_height // (font.size + line_spacing)))

    pages = []
    remaining = question_text.split()
    while remaining:
        chosen: list = []
        for word in remaining:
            candidate = chosen + [word]
            if len(_wrap_text(draw, " ".join(candidate), font, max_width)) > max_lines:
                break
            chosen = candidate
        if not chosen:
            # A single word too wide/tall for one page on its own -- never
            # drop it; give it a page by itself rather than lose it.
            chosen = remaining[:1]
        pages.append(" ".join(chosen))
        remaining = remaining[len(chosen):]

    return pages, floor_size


def render_title_frame(tpl: dict, resolution: tuple, title: str = "", subtitle: str = "") -> Image.Image:
    """The video's intro screen. Deliberately has no introduction
    parameter at all -- the Short Introduction is spoken (see
    build_intro_narration) but must never be drawn on screen, so this
    function is structurally incapable of rendering it, rather than
    relying on a caller to simply not pass it. Call this once with only
    `title` set for the title frame/state, and once with only `subtitle`
    set for the subtitle frame/state (see VideoRenderer.render_intro_segment
    for how the two frames are timed against the narration audio).
    """
    w, h = resolution
    bg_color = tpl["background"]["color"]
    img = Image.new("RGB", (w, h), bg_color)
    draw = ImageDraw.Draw(img)

    intro_layout = tpl["layout"]["intro"]
    fonts = tpl["fonts"]
    max_width = intro_layout["max_width"]
    line_spacing = intro_layout.get("line_spacing", 10)

    if title:
        tf = fonts["intro_title"]
        title_font = load_font(tf["family"], tf["size"])
        _draw_wrapped(draw, title, title_font, intro_layout["title_position"], max_width, tf["color"], line_spacing)

    if subtitle:
        sf = fonts["intro_subtitle"]
        subtitle_font = load_font(sf["family"], sf["size"])
        _draw_wrapped(draw, subtitle, subtitle_font, intro_layout["subtitle_position"], max_width, sf["color"], line_spacing)

    footer_cfg = tpl["layout"].get("footer")
    if footer_cfg:
        ff = tpl["fonts"]["footer"]
        footer_font = load_font(ff["family"], ff["size"])
        fx, fy = footer_cfg["position"]
        draw.text((fx, fy), footer_cfg.get("text", ""), font=footer_font, fill=ff["color"])

    return img
