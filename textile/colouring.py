"""
Graph colouring for textile region maps.

Builds an adjacency graph from a region matrix and applies a greedy
colouring so that no two neighbouring regions share a colour.

Because textile regions are planar graphs, the four colour theorem
guarantees this can always be done with at most 4 colours. Greedy
colouring typically lands at or near that bound.
"""

import numpy as np
from collections import defaultdict


def build_adjacency(region_matrix: np.ndarray) -> dict[int, set[int]]:
    """Build an adjacency map from a region matrix.

    Two regions are adjacent if they share at least one border edge,
    i.e. there exist two grid-neighbouring cells that belong to each.

    Args:
        region_matrix: Integer matrix produced by :func:`determine_regions`.

    Returns:
        A dict mapping each region index to the set of its neighbours.
    """
    rows, cols = region_matrix.shape
    adjacency: dict[int, set[int]] = defaultdict(set)

    # Check every cell against its right and bottom neighbours.
    # If they belong to different regions they are adjacent.
    for r in range(rows):
        for c in range(cols):
            a = int(region_matrix[r, c])
            if c + 1 < cols:
                b = int(region_matrix[r, c + 1])
                if a != b:
                    adjacency[a].add(b)
                    adjacency[b].add(a)
            if r + 1 < rows:
                b = int(region_matrix[r + 1, c])
                if a != b:
                    adjacency[a].add(b)
                    adjacency[b].add(a)

    # Ensure every region has an entry even if it has no neighbours.
    n_regions = int(region_matrix.max())
    for i in range(1, n_regions + 1):
        if i not in adjacency:
            adjacency[i] = set()

    return dict(adjacency)


def greedy_colouring(adjacency: dict[int, set[int]], n_regions: int) -> dict[int, int]:
    """Assign colours to regions using a greedy algorithm.

    Iterates over regions in order and assigns the smallest colour
    (0-indexed integer) not already used by any of its neighbours.

    Args:
        adjacency:  Adjacency map from :func:`build_adjacency`.
        n_regions:  Total number of regions (regions are 1-indexed).

    Returns:
        A dict mapping each region index to its colour index (0-indexed).
    """
    colour_map: dict[int, int] = {}

    for region in range(1, n_regions + 1):
        neighbour_colours = {colour_map[nb] for nb in adjacency.get(region, set())
                             if nb in colour_map}
        colour = 0
        while colour in neighbour_colours:
            colour += 1
        colour_map[region] = colour

    return colour_map


def colour_count(colour_map: dict[int, int]) -> int:
    """Return the number of distinct colours used."""
    return len(set(colour_map.values()))


def make_colour_palette(n_colours: int, seed: int | None = None) -> np.ndarray:
    """Build a random RGBA palette with ``n_colours`` distinct entries.

    Each row is ``[R, G, B, A]`` with values in ``[0, 1]``.

    Args:
        n_colours: Number of colours to generate.
        seed:      Optional seed for reproducibility.

    Returns:
        A float array of shape ``(n_colours, 4)``.
    """
    rng = np.random.default_rng(seed)
    return np.hstack([
        rng.integers(0, 256, size=(n_colours, 3)) / 255.0,
        np.ones((n_colours, 1)),
    ])


def random_colouring(n_regions: int) -> dict[int, int]:
    """Assign a unique colour index to every region (blog-style colouring).

    Each region gets its own distinct colour with no regard for adjacency.
    This is the approach from the original infrahumano blog posts, where
    ``n_regions`` random colours are generated — one per region — producing
    a richer, more varied palette than the minimal greedy colouring.

    Args:
        n_regions: Total number of regions (regions are 1-indexed).

    Returns:
        A dict mapping each region index to a unique colour index (0-indexed).
    """
    return {region: region - 1 for region in range(1, n_regions + 1)}
