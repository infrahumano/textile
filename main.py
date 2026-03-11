"""
Demo entry point for the textile project.

Generates a random textile, prints its region count, and saves
a side-by-side visualization to textile_demo.png.
"""

import numpy as np
from textile import random_textile, symmetric_textile, region_count, determine_regions, plot_side_by_side


def main():
    print("=== textile demo ===\n")

    # Random textile
    N = 80
    matrix = random_textile(N, seed=335)
    regions = determine_regions(matrix)
    n = region_count(regions)
    print(f"Random {N}x{N} textile: {n} regions")

    fig = plot_side_by_side(matrix, color_seed=335)
    fig.savefig("textile_demo.png", dpi=150, bbox_inches="tight")
    print("Saved: textile_demo.png")

    # Symmetric (diagonal) textile
    matrix_sym = symmetric_textile(N, seed=335)
    regions_sym = determine_regions(matrix_sym)
    n_sym = region_count(regions_sym)
    print(f"Symmetric {N}x{N} textile: {n_sym} regions")

    fig_sym = plot_side_by_side(matrix_sym, color_seed=335)
    fig_sym.savefig("textile_demo_symmetric.png", dpi=150, bbox_inches="tight")
    print("Saved: textile_demo_symmetric.png")


if __name__ == "__main__":
    main()
