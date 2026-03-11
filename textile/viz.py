"""
Visualization utilities for textile patterns.

Provides functions to render both the raw textile (line borders) and
the colored region map using matplotlib.
"""

import numpy as np
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.figure import Figure

from .regions import determine_regions, region_count
from .colouring import (
    build_adjacency, greedy_colouring, random_colouring, colour_count,
    make_colour_palette,
)


def plot_regions(
    matrix: np.ndarray,
    color_seed: int | None = None,
    figsize: tuple[float, float] = (10, 10),
    title: str | None = None,
    ax: matplotlib.axes.Axes | None = None,
    colouring: str = "greedy",
) -> tuple[Figure, int]:
    """Plot the coloured region map of a textile.

    Two colouring strategies are available:

    - ``"greedy"`` *(default)*: applies a greedy graph colouring so that no
      two neighbouring regions share a colour, using as few colours as
      possible (typically 4, per the four-colour theorem).
    - ``"random"``: assigns one unique random colour per region with no
      adjacency constraints — the approach from the original infrahumano
      blog posts. Produces a richer, more varied palette.

    Args:
        matrix:     The textile matrix (values in {0, 2, 3, 5}).
        color_seed: Optional seed for reproducible colours.
        figsize:    Figure size (ignored if ax is provided).
        title:      Optional plot title.
        ax:         Optional existing axes to draw into.
        colouring:   Colouring strategy: ``"greedy"`` or ``"random"``.

    Returns:
        A tuple of (Figure, number_of_colours_used).
    """
    if colouring not in ("greedy", "random"):
        raise ValueError(f"colouring must be 'greedy' or 'random', got {colouring!r}")

    region_matrix = determine_regions(matrix)
    n_regions = region_count(region_matrix)

    if colouring == "greedy":
        adjacency = build_adjacency(region_matrix)
        colour_map = greedy_colouring(adjacency, n_regions)
    else:
        colour_map = random_colouring(n_regions)
    n_colours = colour_count(colour_map)

    palette = make_colour_palette(n_colours, seed=color_seed)
    cmap = mcolors.ListedColormap(palette, name="textile_regions", N=n_colours)

    # Build a colour-index matrix (0-indexed) for imshow
    colour_matrix = np.vectorize(colour_map.get)(region_matrix)

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    ax.imshow(colour_matrix, cmap=cmap, vmin=0, vmax=n_colours - 1)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=14)

    return fig, n_colours


def plot_borders(
    matrix: np.ndarray,
    figsize: tuple[float, float] = (8, 8),
    color: str = "orangered",
    title: str | None = None,
    ax: matplotlib.axes.Axes | None = None,
) -> Figure:
    """Plot the raw border structure of a textile as line segments.

    Args:
        matrix:  The textile matrix (values in {0, 2, 3, 5}).
        figsize: Figure size (ignored if ax is provided).
        color:   Line color for borders.
        title:   Optional plot title.
        ax:      Optional existing axes to draw into.

    Returns:
        The matplotlib Figure.
    """
    N = matrix.shape[0]

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    else:
        fig = ax.get_figure()

    for r in range(N):
        for c in range(N):
            val = matrix[r, c]
            # Right border
            if val == 2 or val == 5:
                ax.plot([c + 0.5, c + 0.5], [r - 0.5, r + 0.5], color=color, linewidth=1)
            # Bottom border
            if val == 3 or val == 5:
                ax.plot([c - 0.5, c + 0.5], [r + 0.5, r + 0.5], color=color, linewidth=1)

    ax.set_xlim(-0.5, N - 0.5)
    ax.set_ylim(N - 0.5, -0.5)
    ax.axis("off")
    if title:
        ax.set_title(title, fontsize=14)

    return fig


def plot_side_by_side(
    matrix: np.ndarray,
    color_seed: int | None = None,
    figsize: tuple[float, float] = (16, 8),
    colouring: str = "greedy",
) -> tuple[Figure, int]:
    """Plot the border view and the coloured region view side by side.

    Args:
        matrix:     The textile matrix.
        color_seed: Optional seed for reproducible region colours.
        figsize:    Overall figure size.
        colouring:   Colouring strategy: ``"greedy"`` or ``"random"``.

    Returns:
        A tuple of (Figure, number_of_colours_used).
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    plot_borders(matrix, ax=ax1, title="Borders")
    _, n_colours = plot_regions(
        matrix, color_seed=color_seed, ax=ax2, title="Regions", colouring=colouring
    )
    plt.tight_layout()
    return fig, n_colours
