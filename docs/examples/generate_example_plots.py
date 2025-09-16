"""Generate static SVG previews for the README examples."""
from __future__ import annotations

import math
from pathlib import Path

FONT_STACK = (
    "'CMU Serif', 'Computer Modern', 'Latin Modern Roman', "
    "'Times New Roman', 'Nimbus Roman', serif"
)


def compute_data(samples: int = 400) -> tuple[list[float], list[float]]:
    x_vals = [i * (2 * math.pi) / (samples - 1) for i in range(samples)]
    y_vals = [math.sin(x ** 2) for x in x_vals]
    return x_vals, y_vals


def format_pi(value: float) -> str:
    half_pi = math.pi / 2
    multiples = value / half_pi
    rounded = round(multiples)
    if abs(multiples - rounded) > 1e-6:
        return f"{value:.2f}"
    factor = rounded
    if factor == 0:
        return "0"
    if factor == 1:
        return "½𝜋"
    if factor == 2:
        return "𝜋"
    if factor == 3:
        return "3⁄2·𝜋"
    if factor == 4:
        return "2𝜋"
    return f"{value:.2f}"


def format_tick(value: float) -> str:
    if abs(value) < 1e-9:
        return "0"
    return f"{value:+.1f}".replace("-", "−").replace("+", "")


def map_points(
    xs: list[float],
    ys: list[float],
    *,
    width: int,
    height: int,
    left: int,
    right: int,
    top: int,
    bottom: int,
    y_padding: float = 0.05,
) -> list[tuple[float, float]]:
    x_min, x_max = min(xs), max(xs)
    y_min, y_max = min(ys), max(ys)
    y_span = y_max - y_min
    y_min -= y_span * y_padding
    y_max += y_span * y_padding
    plot_w = width - left - right
    plot_h = height - top - bottom
    mapped = []
    for x, y in zip(xs, ys):
        x_norm = (x - x_min) / (x_max - x_min)
        y_norm = (y - y_min) / (y_max - y_min)
        x_px = left + x_norm * plot_w
        y_px = height - bottom - y_norm * plot_h
        mapped.append((x_px, y_px))
    return mapped


def svg_plot(
    filename: Path,
    *,
    width: int,
    height: int,
    left: int,
    right: int,
    top: int,
    bottom: int,
    title: str,
    subtitle: str,
    side_label: str,
    legend_label: str,
) -> None:
    xs, ys = compute_data()
    coords = map_points(xs, ys, width=width, height=height, left=left, right=right, top=top, bottom=bottom)

    plot_w = width - left - right
    plot_h = height - top - bottom
    x_min, x_max = min(xs), max(xs)
    y_ticks = [-1.0, -0.5, 0.0, 0.5, 1.0]
    x_ticks = [0.0, math.pi / 2, math.pi, 3 * math.pi / 2, 2 * math.pi]

    def x_to_px(val: float) -> float:
        return left + (val - x_min) / (x_max - x_min) * plot_w

    y_min_actual = min(ys)
    y_max_actual = max(ys)
    y_span = y_max_actual - y_min_actual
    y_min = y_min_actual - y_span * 0.05
    y_max = y_max_actual + y_span * 0.05

    def y_to_px(val: float) -> float:
        norm = (val - y_min) / (y_max - y_min)
        return height - bottom - norm * plot_h

    legend_x = left + plot_w * 0.04
    legend_y = top + plot_h * 0.08

    polyline_points = " ".join(f"{x:.2f},{y:.2f}" for x, y in coords)

    svg_parts = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">",
        "  <rect x=\"0\" y=\"0\" width=\"100%\" height=\"100%\" fill=\"#ffffff\" />",
        f"  <style>text {{ font-family: {FONT_STACK}; fill: #1a1a1a; }}</style>",
        f"  <text x=\"{width / 2:.1f}\" y=\"{top * 0.55:.1f}\" font-size=\"24\" text-anchor=\"middle\">{title}</text>",
        f"  <text x=\"{width / 2:.1f}\" y=\"{top * 0.55 + 22:.1f}\" font-size=\"16\" text-anchor=\"middle\" fill=\"#4b4b4b\">{subtitle}</text>",
        f"  <rect x=\"{left}\" y=\"{top}\" width=\"{plot_w}\" height=\"{plot_h}\" fill=\"#fafafa\" stroke=\"#d0d0d0\" stroke-width=\"1\" />",
    ]

    for xt in x_ticks:
        x_px = x_to_px(xt)
        svg_parts.append(
            f"  <line x1=\"{x_px:.2f}\" y1=\"{top}\" x2=\"{x_px:.2f}\" y2=\"{top + plot_h}\" stroke=\"#e4e4e4\" stroke-width=\"1\" stroke-dasharray=\"4 4\" />"
        )
    for yt in y_ticks:
        y_px = y_to_px(yt)
        svg_parts.append(
            f"  <line x1=\"{left}\" y1=\"{y_px:.2f}\" x2=\"{left + plot_w}\" y2=\"{y_px:.2f}\" stroke=\"#e4e4e4\" stroke-width=\"1\" stroke-dasharray=\"4 4\" />"
        )

    svg_parts.extend(
        [
            f"  <text x=\"{left + plot_w / 2:.2f}\" y=\"{height - bottom / 2:.2f}\" font-size=\"18\" text-anchor=\"middle\" font-style=\"italic\">𝑥 (𝑟𝑎𝑑)</text>",
            f"  <text x=\"{left * 0.33:.2f}\" y=\"{top + plot_h / 2:.2f}\" font-size=\"18\" text-anchor=\"middle\" font-style=\"italic\" transform=\"rotate(-90 {left * 0.33:.2f} {top + plot_h / 2:.2f})\">𝑦</text>",
        ]
    )

    for xt in x_ticks:
        x_px = x_to_px(xt)
        label = format_pi(xt)
        svg_parts.append(
            f"  <text x=\"{x_px:.2f}\" y=\"{height - bottom + 24:.2f}\" font-size=\"14\" text-anchor=\"middle\">{label}</text>"
        )
    for yt in y_ticks:
        y_px = y_to_px(yt)
        svg_parts.append(
            f"  <text x=\"{left - 14:.2f}\" y=\"{y_px + 5:.2f}\" font-size=\"14\" text-anchor=\"end\">{format_tick(yt)}</text>"
        )

    svg_parts.append(
        f"  <polyline points=\"{polyline_points}\" fill=\"none\" stroke=\"#1a4f9c\" stroke-width=\"2.5\" />"
    )

    svg_parts.extend(
        [
            f"  <rect x=\"{legend_x - 12:.2f}\" y=\"{legend_y - 18:.2f}\" width=\"188\" height=\"42\" rx=\"6\" ry=\"6\" fill=\"#ffffff\" stroke=\"#c7c7c7\" />",
            f"  <line x1=\"{legend_x:.2f}\" y1=\"{legend_y:.2f}\" x2=\"{legend_x + 62:.2f}\" y2=\"{legend_y:.2f}\" stroke=\"#1a4f9c\" stroke-width=\"2.5\" />",
            f"  <text x=\"{legend_x + 72:.2f}\" y=\"{legend_y + 5:.2f}\" font-size=\"15\" font-style=\"italic\">{legend_label}</text>",
        ]
    )

    svg_parts.append(
        f"  <text x=\"{width / 2:.1f}\" y=\"{height - bottom * 0.25:.1f}\" font-size=\"15\" text-anchor=\"middle\" fill=\"#4b4b4b\">{side_label}</text>"
    )

    svg_parts.append("</svg>")

    filename.write_text("\n".join(svg_parts), encoding="utf-8")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    svg_plot(
        out_dir / "auto_height_no_margins.svg",
        width=900,
        height=600,
        left=84,
        right=44,
        top=86,
        bottom=96,
        title="Example plot",
        subtitle="Auto height • Side margins disabled",
        side_label="export_latex(fig, name=…, fraction=1.0)",
        legend_label="𝑠𝑖𝑛(𝑥²)",
    )
    svg_plot(
        out_dir / "tall_aspect.svg",
        width=900,
        height=840,
        left=84,
        right=44,
        top=86,
        bottom=120,
        title="Example plot",
        subtitle="Fixed aspect = 1.2 (taller)",
        side_label="export_latex(fig, name=…, aspect=1.2)",
        legend_label="𝑠𝑖𝑛(𝑥²)",
    )
    svg_plot(
        out_dir / "wide_margins.svg",
        width=900,
        height=600,
        left=168,
        right=168,
        top=86,
        bottom=96,
        title="Example plot",
        subtitle="Side margin = 0.12",
        side_label="export_latex(fig, name=…, side_margin=0.12)",
        legend_label="𝑠𝑖𝑛(𝑥²)",
    )
