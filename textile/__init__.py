"""
textile — Generate and explore grid-based textile patterns from binary seeds.
"""

from .core import generate_textile, random_textile, symmetric_textile
from .regions import bfs, determine_regions, region_count
from .colouring import (
    build_adjacency, greedy_colouring, random_colouring, colour_count,
    make_colour_palette,
)
from .viz import plot_regions, plot_borders, plot_side_by_side
from .export import to_oxs, save_oxs
from .cli import main as cli_main

__all__ = [
    # core
    "generate_textile",
    "random_textile",
    "symmetric_textile",
    # regions
    "bfs",
    "determine_regions",
    "region_count",
    # colouring
    "build_adjacency",
    "greedy_colouring",
    "random_colouring",
    "colour_count",
    "make_colour_palette",
    # viz
    "plot_regions",
    "plot_borders",
    "plot_side_by_side",
    # export
    "to_oxs",
    "save_oxs",
    # cli
    "cli_main",
]
