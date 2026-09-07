"""Render the last year of contributions as an isometric bar field.

Writes profile-3d-contrib/dark.svg and profile-3d-contrib/light.svg from the
GraphQL contribution calendar. Pure Python, no third-party dependency.
"""

import json
import math
import os
import urllib.request
from datetime import date

USER = "MrlixiangWE"
TOKEN = os.environ.get("GITHUB_TOKEN")
CELL_W = 11.0          # week step in px
CELL_D = 20.0          # weekday step in px
MAX_HEIGHT = 46.0      # tallest bar in px
PAD = 28

THEMES = {
    "dark": {
        "zero": "#161b22", "levels": ["#0e4429", "#006d32", "#26a641", "#39d353"],
        "text": "#c9d1d9", "muted": "#8b949e", "bg": "none",
    },
    "light": {
        "zero": "#ebedf0", "levels": ["#9be9a8", "#40c463", "#30a14e", "#216e39"],
        "text": "#24292f", "muted": "#57606a", "bg": "none",
    },
}


def calendar():
    query = """query($login:String!){ user(login:$login){ contributionsCollection{
        contributionCalendar{ totalContributions weeks{ contributionDays{ date contributionCount weekday } } } } } }"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": USER}}).encode(),
        headers={"Authorization": f"Bearer {TOKEN}", "User-Agent": USER, "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        cal = json.load(resp)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
    return cal["totalContributions"], cal["weeks"]


def shade(hex_color, factor):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c * factor))) for c in (r, g, b))


def scale_for(counts):
    """The 95th percentile of active days, used instead of the raw maximum.

    A single busy day (one merge spree, one import) is enough to push every
    ordinary day below the first quartile, which renders the whole field in
    the darkest shade at minimum height. Capping the scale keeps the four
    colour steps spread across the days that actually vary.
    """
    active = sorted(c for c in counts if c > 0)
    if not active:
        return 1
    return active[min(int(len(active) * 0.95), len(active) - 1)] or 1


def level(count, scale):
    if count <= 0:
        return -1
    q = min(count / scale, 1.0)
    return 0 if q <= 0.25 else 1 if q <= 0.5 else 2 if q <= 0.75 else 3


def iso(w, d):
    """Project grid coordinates (week, weekday) onto the page."""
    x = (w * CELL_W - d * CELL_D) * math.sqrt(3) / 2
    y = (w * CELL_W + d * CELL_D) / 2
    return x, y


def cuboid(w, d, h, color):
    """Three faces of a box whose base cell is (w, d) and height h."""
    ax, ay = iso(w, d)
    bx, by = iso(w + 1, d)
    cx, cy = iso(w + 1, d + 1)
    dx, dy = iso(w, d + 1)
    top = f"{ax},{ay - h} {bx},{by - h} {cx},{cy - h} {dx},{dy - h}"
    left = f"{dx},{dy - h} {cx},{cy - h} {cx},{cy} {dx},{dy}"
    right = f"{cx},{cy - h} {bx},{by - h} {bx},{by} {cx},{cy}"
    return (
        f'<polygon points="{left}" fill="{shade(color, 0.72)}"/>'
        f'<polygon points="{right}" fill="{shade(color, 0.52)}"/>'
        f'<polygon points="{top}" fill="{color}"/>'
    )


def render(total, weeks, theme, path):
    t = THEMES[theme]
    counts = [(wi, day["weekday"], day["contributionCount"], day["date"])
              for wi, week in enumerate(weeks) for day in week["contributionDays"]]
    scale = scale_for([c for _, _, c, _ in counts])
    n_weeks = len(weeks)

    xs, ys = zip(*(iso(w, d) for w in (0, n_weeks) for d in (0, 7)))
    min_x, max_x, min_y, max_y = min(xs), max(xs), min(ys), max(ys)
    width = max_x - min_x + 2 * PAD
    height = max_y - min_y + MAX_HEIGHT + 2 * PAD + 30
    off_x = PAD - min_x
    off_y = PAD + 30 + MAX_HEIGHT - min_y

    boxes = []
    for w, d, c, _ in sorted(counts, key=lambda k: k[0] + k[1]):
        lv = level(c, scale)
        color = t["zero"] if lv < 0 else t["levels"][lv]
        h = 1.5 if lv < 0 else 6 + (MAX_HEIGHT - 6) * min(c / scale, 1.0)
        boxes.append(cuboid(w, d, h, color))

    first = counts[0][3] if counts else ""
    last = counts[-1][3] if counts else ""
    legend = "".join(
        f'<rect x="{width - PAD - 70 + 14 * i}" y="{PAD - 4}" width="10" height="10" rx="2" fill="{col}"/>'
        for i, col in enumerate([t["zero"]] + t["levels"])
    )
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">',
        f'<rect width="100%" height="100%" fill="{t["bg"]}"/>',
        f'<text x="{PAD}" y="{PAD + 6}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="15" font-weight="600" fill="{t["text"]}">{total} contributions</text>',
        f'<text x="{PAD}" y="{PAD + 24}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="11" fill="{t["muted"]}">{first} to {last}, rendered {date.today().isoformat()}</text>',
        f'<text x="{width - PAD - 78}" y="{PAD + 5}" text-anchor="end" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="10" fill="{t["muted"]}">less</text>',
        legend,
        f'<text x="{width - PAD + 4}" y="{PAD + 5}" font-family="Segoe UI,Helvetica,Arial,sans-serif" font-size="10" fill="{t["muted"]}">more</text>',
        f'<g transform="translate({off_x:.1f},{off_y:.1f})" stroke="{t["bg"] if t["bg"] != "none" else "#0d1117"}" stroke-width="0.4" stroke-opacity="0.35">',
        *boxes,
        "</g></svg>",
    ]
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w", encoding="utf-8").write("\n".join(svg))


def main():
    total, weeks = calendar()
    render(total, weeks, "dark", "profile-3d-contrib/dark.svg")
    render(total, weeks, "light", "profile-3d-contrib/light.svg")


if __name__ == "__main__":
    main()
