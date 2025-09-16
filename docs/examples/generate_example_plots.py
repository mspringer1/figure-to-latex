"""Generate static SVG plots for README examples."""
from __future__ import annotations

import math
from pathlib import Path


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
        return "π/2"
    if factor == 2:
        return "π"
    if factor == 3:
        return "3π/2"
    if factor == 4:
        return "2π"
    return f"{value:.2f}"


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

    legend_x = left + plot_w * 0.03
    legend_y = top + plot_h * 0.08

    polyline_points = " ".join(f"{x:.2f},{y:.2f}" for x, y in coords)

    svg_parts = [
        "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
        f"<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"{height}\" viewBox=\"0 0 {width} {height}\">",
        "  <rect x=\"0\" y=\"0\" width=\"100%\" height=\"100%\" fill=\"#ffffff\" />",
        "  <style>text { font-family: 'DejaVu Sans', Arial, sans-serif; fill: #222; }</style>",
        f"  <text x=\"{width / 2:.1f}\" y=\"{top * 0.55:.1f}\" font-size=\"24\" text-anchor=\"middle\">{title}</text>",
        f"  <text x=\"{width / 2:.1f}\" y=\"{top * 0.55 + 24:.1f}\" font-size=\"16\" text-anchor=\"middle\" fill=\"#555\">{subtitle}</text>",
        f"  <rect x=\"{left}\" y=\"{top}\" width=\"{plot_w}\" height=\"{plot_h}\" fill=\"#fafafa\" stroke=\"#d0d0d0\" stroke-width=\"1\" />",
    ]

    for xt in x_ticks:
        x_px = x_to_px(xt)
        svg_parts.append(
            f"  <line x1=\"{x_px:.2f}\" y1=\"{top}\" x2=\"{x_px:.2f}\" y2=\"{top + plot_h}\" stroke=\"#e0e0e0\" stroke-width=\"1\" stroke-dasharray=\"4 4\" />"
        )
    for yt in y_ticks:
        y_px = y_to_px(yt)
        svg_parts.append(
            f"  <line x1=\"{left}\" y1=\"{y_px:.2f}\" x2=\"{left + plot_w}\" y2=\"{y_px:.2f}\" stroke=\"#e0e0e0\" stroke-width=\"1\" stroke-dasharray=\"4 4\" />"
        )

    svg_parts.extend(
        [
            f"  <text x=\"{left + plot_w / 2:.2f}\" y=\"{height - bottom / 2:.2f}\" font-size=\"18\" text-anchor=\"middle\">X axis label</text>",
            f"  <text x=\"{left * 0.35:.2f}\" y=\"{top + plot_h / 2:.2f}\" font-size=\"18\" text-anchor=\"middle\" transform=\"rotate(-90 {left * 0.35:.2f} {top + plot_h / 2:.2f})\">Y axis label</text>",
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
            f"  <text x=\"{left - 12:.2f}\" y=\"{y_px + 5:.2f}\" font-size=\"14\" text-anchor=\"end\">{yt:g}</text>"
        )

    svg_parts.append(
        f"  <polyline points=\"{polyline_points}\" fill=\"none\" stroke=\"#1f77b4\" stroke-width=\"2.5\" />"
    )

    svg_parts.extend(
        [
            f"  <rect x=\"{legend_x - 10:.2f}\" y=\"{legend_y - 18:.2f}\" width=\"180\" height=\"40\" rx=\"6\" ry=\"6\" fill=\"#ffffff\" stroke=\"#d0d0d0\" />",
            f"  <line x1=\"{legend_x:.2f}\" y1=\"{legend_y:.2f}\" x2=\"{legend_x + 60:.2f}\" y2=\"{legend_y:.2f}\" stroke=\"#1f77b4\" stroke-width=\"2.5\" />",
            f"  <text x=\"{legend_x + 70:.2f}\" y=\"{legend_y + 5:.2f}\" font-size=\"15\">{legend_label}</text>",
        ]
    )

    svg_parts.append(
        f"  <text x=\"{width / 2:.1f}\" y=\"{height - bottom * 0.25:.1f}\" font-size=\"15\" text-anchor=\"middle\" fill=\"#666\">{side_label}</text>"
    )

    svg_parts.append("</svg>")

    filename.write_text("\n".join(svg_parts), encoding="utf-8")


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent
    svg_plot(
        out_dir / "auto_height_no_margins.svg",
        width=900,
        height=600,
        left=80,
        right=40,
        top=80,
        bottom=90,
        title="Example Plot",
        subtitle="Auto height • Side margins disabled",
        side_label="export_latex(fig, name=..., fraction=1.0)",
        legend_label="Sine wave",
    )
    svg_plot(
        out_dir / "tall_aspect.svg",
        width=900,
        height=840,
        left=80,
        right=40,
        top=80,
        bottom=110,
        title="Example Plot",
        subtitle="Fixed aspect = 1.2 (taller)",
        side_label="export_latex(fig, name=..., aspect=1.2)",
        legend_label="Sine wave",
    )
    svg_plot(
        out_dir / "wide_margins.svg",
        width=900,
        height=600,
        left=160,
        right=160,
        top=80,
        bottom=90,
        title="Example Plot",
        subtitle="Side margin = 0.12",
        side_label="export_latex(fig, name=..., side_margin=0.12)",
        legend_label="Sine wave",
    )
