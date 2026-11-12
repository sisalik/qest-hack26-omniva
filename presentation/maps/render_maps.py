# /// script
# requires-python = ">=3.12"
# dependencies = ["cairosvg", "contextily", "httpx", "matplotlib", "python-dotenv"]
# ///
"""Render route maps for the slides on a MapTiler Dataviz basemap.

Reads map definitions from routes.json and writes one PNG per map to
presentation/img/. Routes are straight lines labelled with the symmetrised
distance the solvers use: D[min(i, j)][max(i, j)]. Tiles, fonts and the logo
are cached in .cache/, so re-renders while tweaking the style run offline.

Run from anywhere: uv run presentation/maps/render_maps.py
"""

import io
import json
import math
from pathlib import Path

import cairosvg
import contextily as ctx
import httpx
import matplotlib.patheffects as pe
import matplotlib.pyplot as plt
from dotenv import dotenv_values
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.path import Path as MplPath

MAPS_DIR = Path(__file__).resolve().parent
REPO_ROOT = MAPS_DIR.parents[1]
CACHE_DIR = MAPS_DIR / ".cache"
OUT_DIR = MAPS_DIR.parent / "img"
MATRIX_FILE = REPO_ROOT / "tallinn_osrm_matrix.json"

# 256/ selects the 256 px tile grid (1 billed request per tile instead of 4 for
# the default 512 px grid); @2x still returns 512 px images for sharp output.
TILE_URL = "https://api.maptiler.com/maps/dataviz/256/{z}/{x}/{y}@2x.png?key="
TILE_PIXELS = 512
LOGO_URL = "https://api.maptiler.com/resources/logo.svg"
ATTRIBUTION = "© MapTiler © OpenStreetMap contributors"
FONT_URL = "https://cdn.jsdelivr.net/fontsource/fonts/inter@5.2.5/latin-{weight}-normal.ttf"

EARTH_RADIUS_M = 6378137
FIG_WIDTH_IN = 16
# A single map fills a 16:9 slide; side-by-side panels use a lower figure so the
# image leaves room for the slide heading.
SINGLE_HEIGHT_IN = 9
PANELS_HEIGHT_IN = 7
PANEL_GAP = 0.008
DPI = 150

PILL_FONTSIZE = 12
STOP_MARKER_SIZE = 700
DEPOT_MARKER_SIZE = 1100
# Warehouse pictogram for the depot badge: a gabled building with a garage door
# opening, and two door slats drawn as separate shapes inside the opening.
WAREHOUSE_ICON = MplPath.make_compound_path(
    MplPath([(-0.5, -0.5), (-0.28, -0.5), (-0.28, 0.02), (0.28, 0.02), (0.28, -0.5), (0.5, -0.5), (0.5, 0.18), (0, 0.5), (-0.5, 0.18), (-0.5, -0.5)], closed=True),
    MplPath([(-0.18, -0.12), (0.18, -0.12), (0.18, -0.05), (-0.18, -0.05), (-0.18, -0.12)], closed=True),
    MplPath([(-0.18, -0.3), (0.18, -0.3), (0.18, -0.23), (-0.18, -0.23), (-0.18, -0.3)], closed=True),
)
MARKER_DIAMETER_PX = math.sqrt(STOP_MARKER_SIZE) * DPI / 72

NAVY = "#14213D"
ROUTE_COLOURS = ["#B5541C", "#2B6CB0", "#2F855A"]


def cached_download(url: str, filename: str) -> Path:
    path = CACHE_DIR / filename
    if not path.exists():
        response = httpx.get(url, timeout=30)
        response.raise_for_status()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(response.content)
    return path


def use_inter_font() -> None:
    """Match the deck's typeface; Inter is rarely installed system-wide."""
    for weight in (400, 600):
        font_manager.fontManager.addfont(cached_download(FONT_URL.format(weight=weight), f"inter-{weight}.ttf"))
    plt.rcParams["font.family"] = "Inter"


def maptiler_logo():
    svg = cached_download(LOGO_URL, "maptiler-logo.svg").read_bytes()
    return plt.imread(io.BytesIO(cairosvg.svg2png(bytestring=svg, scale=2)))


def to_mercator(lon: float, lat: float) -> tuple[float, float]:
    x = math.radians(lon) * EARTH_RADIUS_M
    y = math.log(math.tan(math.pi / 4 + math.radians(lat) / 2)) * EARTH_RADIUS_M
    return x, y


def panels_of(spec: dict) -> list[dict]:
    """A map is either one panel ("routes") or several side by side ("panels")."""
    return spec.get("panels") or [{"routes": spec["routes"]}]


def load_maps(point_count: int) -> list[dict]:
    maps = json.loads((MAPS_DIR / "routes.json").read_text())["maps"]
    for m in maps:
        for route in (r for panel in panels_of(m) for r in panel["routes"]):
            stops = route["stops"]
            if len(stops) < 2:
                raise ValueError(f"{m['name']}/{route['label']}: a route needs at least 2 stops")
            bad = [s for s in stops if not 0 <= s < point_count]
            if bad:
                raise ValueError(f"{m['name']}/{route['label']}: unknown point indices {bad}")
    return maps


def edge_km(distances: list[list[int]], a: int, b: int) -> float:
    return distances[min(a, b)][max(a, b)] / 1000


def fit_extent(xs: list[float], ys: list[float], aspect: float, pad: float = 0.25) -> tuple[float, float, float, float]:
    """Pad the bounding box and widen it to the panel's aspect ratio."""
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    w, h = (x1 - x0) * (1 + 2 * pad), (y1 - y0) * (1 + 2 * pad)
    w, h = max(w, h * aspect), max(h, w / aspect)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    return cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


def tile_zoom(extent_width_m: float, out_px: float) -> int:
    """Lowest zoom whose tiles are at least as sharp as the output image."""
    return min(18, math.ceil(math.log2(2 * math.pi * EARTH_RADIUS_M * out_px / (TILE_PIXELS * extent_width_m))))


def readable_angle(dx: float, dy: float) -> float:
    """Angle of a segment in degrees, flipped so text along it is never upside down."""
    angle = math.degrees(math.atan2(dy, dx))
    if angle > 90:
        return angle - 180
    if angle < -90:
        return angle + 180
    return angle


Box = tuple[float, float, float, float]


def overlap_area(a: Box, b: Box) -> float:
    return max(0, min(a[2], b[2]) - max(a[0], b[0])) * max(0, min(a[3], b[3]) - max(a[1], b[1]))


def label_stop(ax, xy: tuple[float, float], neighbours: list[tuple[float, float]], obstacles: list[Box], text: str, **text_kw) -> Box:
    """Place a name label on the side of the marker facing away from its route lines.

    Tries eight compass directions, best aligned with the outward direction first.
    A label that would cross the panel's left or right edge slides back inside.
    Of the directions that keep the label inside the panel, takes the one that
    overlaps obstacles (pixel boxes of markers and labels) least, preferring the
    outward one on ties. Returns the label's pixel box.
    """
    to_px = ax.transData.transform
    px, py = to_px(xy)
    outward_x = outward_y = 0.0
    for n in neighbours:
        nx, ny = to_px(n)
        length = math.hypot(px - nx, py - ny) or 1
        outward_x += (px - nx) / length
        outward_y += (py - ny) / length
    if math.hypot(outward_x, outward_y) < 0.3:
        outward_x, outward_y = 0.0, 1.0

    px_per_pt = DPI / 72
    probe = ax.text(0, 0, text, **text_kw)
    extent = probe.get_window_extent(ax.figure.canvas.get_renderer())
    probe.remove()
    width, height = extent.width, extent.height
    offset = 20 * px_per_pt
    margin = 12 * px_per_pt
    bounds = ax.get_window_extent()
    panel_x0, panel_y0, panel_x1, panel_y1 = bounds.x0 + margin, bounds.y0 + margin, bounds.x1 - margin, bounds.y1 - margin
    candidates = [(math.cos(math.radians(a)), math.sin(math.radians(a))) for a in range(0, 360, 45)]
    candidates.sort(key=lambda d: -(d[0] * outward_x + d[1] * outward_y))
    placements = []
    for dx, dy in candidates:
        ha = "left" if dx > 0.3 else "right" if dx < -0.3 else "center"
        va = "bottom" if dy > 0.3 else "top" if dy < -0.3 else "center"
        ax_x, ax_y = px + dx * offset, py + dy * offset
        left = {"left": ax_x, "right": ax_x - width, "center": ax_x - width / 2}[ha]
        bottom = {"bottom": ax_y, "top": ax_y - height, "center": ax_y - height / 2}[va]
        slide = max(0, panel_x0 - left) - max(0, left + width - panel_x1)
        left, ax_x = left + slide, ax_x + slide
        box = (left, bottom, left + width, bottom + height)
        own_marker = (px - MARKER_DIAMETER_PX / 2, py - MARKER_DIAMETER_PX / 2, px + MARKER_DIAMETER_PX / 2, py + MARKER_DIAMETER_PX / 2)
        if left < panel_x0 or bottom < panel_y0 or box[3] > panel_y1 or overlap_area(box, own_marker):
            continue
        placements.append((sum(overlap_area(box, o) for o in obstacles), (ax_x - px, ax_y - py), ha, va, box))
    _, (off_x, off_y), ha, va, box = min(placements, key=lambda p: p[0])
    ax.annotate(text, xy, xytext=(off_x / px_per_pt, off_y / px_per_pt), textcoords="offset points", ha=ha, va=va, **text_kw)
    return box


def draw_panel(ax, routes: list[dict], colours: list[str], matrix: dict, extent: tuple[float, float, float, float], tile_url: str) -> None:
    points, distances = matrix["points"], matrix["distances"]
    stop_xy = {i: to_mercator(p["lon"], p["lat"]) for i, p in enumerate(points)}
    x0, x1, y0, y1 = extent
    ax.set_axis_off()
    ax.set_xlim(x0, x1)
    ax.set_ylim(y0, y1)
    ctx.add_basemap(ax, source=tile_url, zoom=tile_zoom(x1 - x0, ax.get_window_extent().width), attribution=False)

    halo = [pe.withStroke(linewidth=4, foreground="white")]
    to_px = ax.transData.transform
    radius = MARKER_DIAMETER_PX / 2
    obstacles: list[Box] = []
    for s in {s for route in routes for s in route["stops"]}:
        x, y = to_px(stop_xy[s])
        obstacles.append((x - radius, y - radius, x + radius, y + radius))
    legend_handles, legend_labels = [], []
    for colour, route in zip(colours, routes):
        stops = route["stops"]
        xs, ys = zip(*(stop_xy[s] for s in stops))
        ax.plot(xs, ys, color="white", linewidth=8, solid_capstyle="round", solid_joinstyle="round", zorder=2)
        ax.plot(xs, ys, color=colour, linewidth=4, solid_capstyle="round", solid_joinstyle="round", zorder=3)

        legs = list(zip(stops, stops[1:]))
        for a, b in legs:
            (ax_, ay), (bx, by) = ax.transData.transform(stop_xy[a]), ax.transData.transform(stop_xy[b])
            length = math.hypot(bx - ax_, by - ay) or 1
            text = f"{edge_km(distances, a, b):.1f} km"
            # A pill that does not fit between the two markers sits beside the leg instead of on it.
            pill_px = (len(text) * 0.6 + 1.5) * PILL_FONTSIZE * DPI / 72
            shift = 0 if length >= pill_px + MARKER_DIAMETER_PX else 1.6 * PILL_FONTSIZE * DPI / 72
            normal_x, normal_y = -(by - ay) / length, (bx - ax_) / length
            if normal_y < 0:
                normal_x, normal_y = -normal_x, -normal_y
            cx, cy = (ax_ + bx) / 2 + normal_x * shift, (ay + by) / 2 + normal_y * shift
            pill = ax.annotate(
                text, (cx, cy), xycoords="figure pixels",
                rotation=readable_angle(bx - ax_, by - ay), rotation_mode="anchor", ha="center", va="center",
                fontsize=PILL_FONTSIZE, fontweight=600, color=NAVY, zorder=4,
                bbox={"boxstyle": "round,pad=0.35,rounding_size=0.8", "facecolor": "white", "edgecolor": colour, "linewidth": 1.5},
            )
            # The text's box excludes the rounded frame around it, hence the padding.
            text_box = pill.get_window_extent(ax.figure.canvas.get_renderer())
            frame = 0.5 * PILL_FONTSIZE * DPI / 72
            obstacles.append((text_box.x0 - frame, text_box.y0 - frame, text_box.x1 + frame, text_box.y1 + frame))

        for order, i in enumerate(range(1, len(stops) - 1), start=1):
            x, y = stop_xy[stops[i]]
            ax.scatter(x, y, s=STOP_MARKER_SIZE, color=colour, edgecolors="white", linewidths=2.5, zorder=5)
            ax.text(x, y, str(order), color="white", fontsize=15, fontweight=600, ha="center", va="center", zorder=6)
            obstacles.append(label_stop(ax, (x, y), [stop_xy[stops[i - 1]], stop_xy[stops[i + 1]]], obstacles, points[stops[i]]["name"], fontsize=15, color=NAVY, path_effects=halo, zorder=6))

        total_km = sum(edge_km(distances, a, b) for a, b in legs)
        legend_handles.append(Line2D([], [], color=colour, linewidth=4, solid_capstyle="round"))
        legend_labels.append(f"{route['label']}  ·  {total_km:.1f} km")

    for depot in {route["stops"][0] for route in routes}:
        x, y = stop_xy[depot]
        ax.scatter(x, y, s=DEPOT_MARKER_SIZE, color=NAVY, edgecolors="white", linewidths=2.5, zorder=5)
        ax.scatter(x, y, s=DEPOT_MARKER_SIZE * 0.3, marker=WAREHOUSE_ICON, color="white", linewidths=0, zorder=6)
        neighbours = [stop_xy[r["stops"][j]] for r in routes if r["stops"][0] == depot for j in (1, -2)]
        obstacles.append(label_stop(ax, (x, y), neighbours, obstacles, "Depot", fontsize=15, fontweight=600, color=NAVY, path_effects=halo, zorder=6))

    legend = ax.legend(legend_handles, legend_labels, loc="upper left", fontsize=16, handlelength=1.6, borderpad=0.9, borderaxespad=1.2, fancybox=True, framealpha=0.92, edgecolor="none")
    legend.set_zorder(10)


def render_map(spec: dict, matrix: dict, tile_url: str, logo) -> Path:
    panels = panels_of(spec)
    fig_h = SINGLE_HEIGHT_IN if len(panels) == 1 else PANELS_HEIGHT_IN
    panel_w = (1 - PANEL_GAP * (len(panels) - 1)) / len(panels)
    aspect = FIG_WIDTH_IN * panel_w / fig_h

    # All panels share one map area so the routes are directly comparable.
    stop_xy = [to_mercator(p["lon"], p["lat"]) for p in matrix["points"]]
    used = {s for panel in panels for route in panel["routes"] for s in route["stops"]}
    extent = fit_extent([stop_xy[s][0] for s in used], [stop_xy[s][1] for s in used], aspect)

    fig = plt.figure(figsize=(FIG_WIDTH_IN, fig_h), dpi=DPI)
    colours = iter(ROUTE_COLOURS)
    for n, panel in enumerate(panels):
        ax = fig.add_axes((n * (panel_w + PANEL_GAP), 0, panel_w, 1))
        draw_panel(ax, panel["routes"], [next(colours) for _ in panel["routes"]], matrix, extent, tile_url)

    fig.figimage(logo, xo=24, yo=24, zorder=10)
    ax.text(0.99, 0.01, ATTRIBUTION, transform=ax.transAxes, ha="right", va="bottom", fontsize=11, color="#4A5568", bbox={"facecolor": "white", "alpha": 0.8, "edgecolor": "none", "pad": 3}, zorder=10)

    out_path = OUT_DIR / f"{spec['name']}.png"
    fig.savefig(out_path)
    plt.close(fig)
    return out_path


def main() -> None:
    key = dotenv_values(REPO_ROOT / ".env").get("MAPTILER_KEY")
    if not key:
        raise SystemExit(f"MAPTILER_KEY is missing from {REPO_ROOT / '.env'}")
    ctx.set_cache_dir(str(CACHE_DIR / "tiles"))
    use_inter_font()
    matrix = json.loads(MATRIX_FILE.read_text())
    logo = maptiler_logo()
    for spec in load_maps(len(matrix["points"])):
        print(f"Rendered {render_map(spec, matrix, TILE_URL + key, logo).relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    main()
