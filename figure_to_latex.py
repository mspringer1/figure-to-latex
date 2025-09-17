from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Tuple, Union

import matplotlib as mpl
import matplotlib.pyplot as plt


__all__ = ["configure_latex", "export_latex"]

# --------------------------------------------------------------------
# Project-wide settings
# --------------------------------------------------------------------
# Set this once to your LaTeX document's \textwidth (TeX points; 72.27 pt = 1 in)
TEXTWIDTH_PT: float = 345.0

_DEFAULTS: Dict[str, Any] = {
    # TeX engine / fonts
    "engine": "pdflatex",               # or "lualatex", "xelatex"
    "family": "serif",
    "serif": ["Computer Modern"],

    # Font sizes (pt)
    "base_font_pt": 11,
    "axes_label_pt": None,              # None -> use base_font_pt
    "tick_font_pt": 10,
    "legend_font_pt": 10,

    # TeX integration
    "use_tex": True,
    "use_mathtext_for_ticks": False,
    "preamble": r"""
        \usepackage{amsmath}
        \usepackage{amssymb}
        \usepackage{siunitx}\sisetup{detect-all}
        \providecommand{\mathdefault}[1]{#1}
    """,

    # Optional outer margins (fraction of figure width). None => disabled.
    "side_margin": None,                # float or (left, right)
}


def _apply_rc() -> None:
    """Apply rcParams from _DEFAULTS."""
    mpl.rcParams.update({
        "text.usetex": _DEFAULTS["use_tex"],
        "font.family": _DEFAULTS["family"],
        "font.serif": _DEFAULTS["serif"],
        "font.size": _DEFAULTS["base_font_pt"],
        "axes.labelsize": (
            _DEFAULTS["axes_label_pt"]
            if _DEFAULTS["axes_label_pt"] is not None
            else _DEFAULTS["base_font_pt"]
        ),
        "legend.fontsize": _DEFAULTS["legend_font_pt"],
        "xtick.labelsize": _DEFAULTS["tick_font_pt"],
        "ytick.labelsize": _DEFAULTS["tick_font_pt"],
        "axes.formatter.use_mathtext": _DEFAULTS["use_mathtext_for_ticks"],
        # PGF backend
        "pgf.texsystem": _DEFAULTS["engine"],
        "pgf.rcfonts": False,
        "pgf.preamble": _DEFAULTS["preamble"],
    })


_apply_rc()


def configure_latex(
    *,
    textwidth_pt: Optional[float] = None,
    engine: Optional[str] = None,
    base_font_pt: Optional[int] = None,
    axes_label_pt: Optional[int] = None,
    tick_font_pt: Optional[int] = None,
    legend_font_pt: Optional[int] = None,
    family: Optional[str] = None,
    serif: Optional[Iterable[str]] = None,
    preamble: Optional[str] = None,
    use_tex: Optional[bool] = None,
    use_mathtext_for_ticks: Optional[bool] = None,
    side_margin: Optional[Union[float, Tuple[float, float]]] = None,
) -> None:
    """
    Configure project-wide LaTeX/PGF settings once (call near program start).
    """
    global TEXTWIDTH_PT
    if textwidth_pt is not None:
        TEXTWIDTH_PT = float(textwidth_pt)
    if engine is not None:
        _DEFAULTS["engine"] = engine
    if base_font_pt is not None:
        _DEFAULTS["base_font_pt"] = int(base_font_pt)
    if axes_label_pt is not None:
        _DEFAULTS["axes_label_pt"] = int(axes_label_pt)
    if tick_font_pt is not None:
        _DEFAULTS["tick_font_pt"] = int(tick_font_pt)
    if legend_font_pt is not None:
        _DEFAULTS["legend_font_pt"] = int(legend_font_pt)
    if family is not None:
        _DEFAULTS["family"] = family
    if serif is not None:
        _DEFAULTS["serif"] = list(serif)
    if preamble is not None:
        _DEFAULTS["preamble"] = preamble
    if use_tex is not None:
        _DEFAULTS["use_tex"] = bool(use_tex)
    if use_mathtext_for_ticks is not None:
        _DEFAULTS["use_mathtext_for_ticks"] = bool(use_mathtext_for_ticks)
    if side_margin is not None:
        _DEFAULTS["side_margin"] = side_margin

    _apply_rc()


def _pt_to_in(pt: float) -> float:
    return float(pt) / 72.27


def export_latex(
    fig: mpl.figure.Figure,
    *,
    name: Union[str, Path],
    fraction: float = 1.0,
    aspect: Optional[float] = None,
    show: bool = True,
    formats: Iterable[str] = ("pgf",),
    dpi: Optional[int] = None,
    bbox_inches: Optional[str] = None,
    # per-call font overrides
    font_size: Optional[int] = None,
    axes_label_size: Optional[int] = None,
    tick_size: Optional[int] = None,
    legend_size: Optional[int] = None,
    # per-plot margins (None -> use project default)
    side_margin: Optional[Union[float, Tuple[float, float]]] = None,
    # tiny debug helper
    debug: bool = False,
) -> Path:
    """
    Export a Matplotlib figure to LaTeX-ready PGF (and optional formats)
    with exact on-screen parity (same size/appearance).

    Parameters
    ----------
    fig : matplotlib.figure.Figure
        The Matplotlib figure to finalize and save.
    name : str or Path
        Basename or path for the output file(s). Do not include an extension:
          - "example" -> saves "example.pgf" (and other formats) in the current dir
          - "figures/example" -> saves "figures/example.pgf" etc. (creates folder if needed)
    fraction : float, default=1.0
        Fraction of LaTeX \\textwidth to occupy. 1.0 = full \\textwidth.
    aspect : float or None, default=None
        Height/width. If None, use the figure's current ratio (error if unknown).
    show : bool, default=True
        If True, opens an interactive preview (same size as PGF export).
    formats : iterable of str, default=("pgf",)
        File formats to save (e.g. "pgf", "pdf", "png").
    dpi : int, optional
        Resolution for raster outputs (PNG, etc.).
    bbox_inches : str, optional
        Passed to `fig.savefig`. Use "tight" to trim whitespace.
    font_size, axes_label_size, tick_size, legend_size : int, optional
        Per-call font size overrides (otherwise global defaults).
    side_margin : float, (float, float), or None
        Extra outer margin as fraction of figure width.
        None -> use global default (see `configure_latex`); if that is also None, no margins.
    debug : bool, default=False
        Print inferred aspect ratio and applied margins.

    Returns
    -------
    Path
        Path of the first saved file (typically the .pgf).
    """
    # Decide aspect from current fig if not provided
    if aspect is None:
        wi, hi = fig.get_size_inches()
        if wi <= 0:
            raise ValueError("Figure width is zero; cannot infer aspect ratio. "
                             "Provide aspect explicitly.")
        aspect = hi / wi
        if debug:
            print(f"[export_latex] aspect inferred = {aspect:.3f}")

    # Fix physical size to match LaTeX width (never scale in LaTeX)
    width_in = _pt_to_in(TEXTWIDTH_PT) * float(fraction)
    height_in = width_in * float(aspect)
    fig.set_size_inches(width_in, height_in, forward=True)

    # Optional outer side margins
    sm = _DEFAULTS["side_margin"] if side_margin is None else side_margin
    if sm is not None:
        if isinstance(sm, (tuple, list)):
            left_frac, right_frac = float(sm[0]), float(sm[1])
        else:
            left_frac = right_frac = float(sm)
        left = max(0.0, min(1.0, left_frac))
        right = 1.0 - max(0.0, min(1.0, right_frac))
        fig.subplots_adjust(left=left, right=right)
        if debug:
            print(f"[export_latex] side margins set to left={left_frac:.3f}, right={right_frac:.3f}")

    # Optional, temporary font overrides
    overrides: Dict[str, Any] = {}
    if font_size is not None:
        overrides["font.size"] = font_size
    if axes_label_size is not None:
        overrides["axes.labelsize"] = axes_label_size
    if tick_size is not None:
        overrides["xtick.labelsize"] = overrides["ytick.labelsize"] = tick_size
    if legend_size is not None:
        overrides["legend.fontsize"] = legend_size

    base = Path(name)

    def _save_all() -> Path:
        first_path: Optional[Path] = None
        for fmt in formats:
            fp = base.with_suffix(f".{fmt}")
            fp.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(fp, dpi=dpi, bbox_inches=bbox_inches)
            if first_path is None:
                first_path = fp
        assert first_path is not None
        return first_path

    # Draw then save
    if overrides:
        with mpl.rc_context(rc=overrides):
            fig.canvas.draw()
            first = _save_all()
    else:
        fig.canvas.draw()
        first = _save_all()

    if show:
        plt.show()
    plt.close(fig)
    return first
