from pathlib import Path
import textwrap

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "assets"
FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"
BOLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
INK = "#17324d"
LINE = "#d5dde5"


def font(size, bold=False):
    return ImageFont.truetype(BOLD if bold else FONT, size)


def wrapped(draw, xy, text, width, size=20, bold=False, fill=INK, spacing=5):
    lines = textwrap.wrap(text, width=width)
    draw.multiline_text(xy, "\n".join(lines), font=font(size, bold), fill=fill, spacing=spacing)


def card(draw, box, title, body, color):
    draw.rounded_rectangle(box, 10, fill="white", outline=LINE, width=2)
    draw.rounded_rectangle((box[0], box[1], box[0] + 7, box[3]), 4, fill=color)
    draw.text((box[0] + 18, box[1] + 13), title, font=font(17, True), fill=INK)
    wrapped(draw, (box[0] + 18, box[1] + 42), body, 24, 16)


def render_week2():
    image = Image.new("RGB", (1400, 700), "white")
    draw = ImageDraw.Draw(image)
    draw.text((42, 28), "End of Week 2 Scrum Board", font=font(46, True), fill=INK)
    draw.text((42, 87), "Evidence checkpoint 29 October 2026 | Done requires artifact and test evidence", font=font(20), fill="#526577")
    labels = ["Backlog", "To Do", "In Progress", "Blocked", "Done"]
    x0, y0, gap, width, height = 42, 137, 14, 252, 520
    for index, label in enumerate(labels):
        x = x0 + index * (width + gap)
        fill = "#fde7e7" if label == "Blocked" else "#dff3e8" if label == "Done" else "#eaf0f5"
        draw.rounded_rectangle((x, y0, x + width, y0 + height), 12, fill="#f8fafc", outline=LINE, width=2)
        draw.rounded_rectangle((x, y0, x + width, y0 + 62), 12, fill=fill)
        draw.text((x + 18, y0 + 19), label, font=font(22, True), fill=INK)
    blocked_x = x0 + 3 * (width + gap)
    card(draw, (blocked_x + 13, y0 + 82, blocked_x + width - 13, y0 + 242), "T13 M5", "Streamlit Cloud deployment. Remote authorization and a verified public URL are required.", "#d04348")
    done_x = x0 + 4 * (width + gap)
    done_cards = [
        ("T01 T02 T03 M1", "Requirements and final records"),
        ("T04 T05 M2", "Navigation and comparison"),
        ("T06 T07 M3", "Market data and risk dashboard"),
        ("T08 T09 T10 M4", "Feasibility, MVP and validation"),
        ("T11 T12 M5", "Environment and integration"),
    ]
    top = y0 + 77
    for title, body in done_cards:
        card(draw, (done_x + 12, top, done_x + width - 12, top + 79), title, body, "#18834b")
        top += 87
    image.save(OUT / "scrum_end_week2.png", quality=95)


def status_box(draw, box, title, items, fill):
    draw.rounded_rectangle(box, 10, fill=fill)
    draw.text((box[0] + 16, box[1] + 14), title, font=font(18, True), fill=INK)
    y = box[1] + 50
    for item in items:
        draw.text((box[0] + 18, y), item, font=font(17), fill=INK)
        y += 31


def snapshot(draw, x, title, groups):
    draw.rounded_rectangle((x, 142, x + 450, 606), 12, fill="#fbfcfd", outline=LINE, width=2)
    draw.text((x + 20, 166), title, font=font(25, True), fill=INK)
    box_width = 127
    for index, (name, items, fill) in enumerate(groups):
        left = x + 20 + index * 139
        status_box(draw, (left, 214, left + box_width, 566), name, items, fill)


def render_comparison():
    image = Image.new("RGB", (1500, 650), "white")
    draw = ImageDraw.Draw(image)
    draw.text((38, 30), "PD2 Scrum Progress Comparison", font=font(44, True), fill=INK)
    draw.text((38, 88), "Historical snapshots preserved | Week 2 follows the final task mapping", font=font(20), fill="#526577")
    snapshot(draw, 38, "Before Week 1 Planned", [
        ("To Do", ["T01 T02", "T04 T05", "T06 T07", "T08 T11"], "#fff4d6"),
        ("Backlog", ["T03", "T09 T10", "T12 T13"], "#edf1f5"),
        ("Done", ["None"], "#dff3e8"),
    ])
    snapshot(draw, 518, "End of Week 1 Actual", [
        ("Done", ["T01 T02", "T04 T05", "T06 T07", "T08 T11"], "#dff3e8"),
        ("Remaining", ["T03", "T09 T10", "T12 T13"], "#fff4d6"),
        ("Blocked", ["None"], "#fde7e7"),
    ])
    snapshot(draw, 998, "End of Week 2 Actual", [
        ("Done", ["T01-T12", "except T13", "23 tests pass"], "#dff3e8"),
        ("Remaining", ["Time entries", "Team feedback"], "#fff4d6"),
        ("Blocked", ["T13 Cloud", "Authorization", "Public URL"], "#fde7e7"),
    ])
    image.save(OUT / "scrum_progress_comparison.png", quality=95)


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    render_week2()
    render_comparison()
