"""
Core textile generation.

A textile is represented as an NxN matrix with entries in {0, 2, 3, 5}:
  - 0: no border
  - 2: border on the right
  - 3: border on the bottom
  - 5: border on both right and bottom (2 + 3)

Given a row_seed and col_seed (1D binary numpy arrays of length N), the
textile encodes which cells have horizontal and vertical line segments
separating them from their neighbours.
"""

import numpy as np


def generate_textile(N: int, row_seed: np.ndarray, col_seed: np.ndarray) -> np.ndarray:
    """Generate an NxN textile matrix from two binary seed arrays.

    Args:
        N:        Size of the grid (N x N).
        row_seed: Binary array of length N controlling horizontal borders.
        col_seed: Binary array of length N controlling vertical borders.

    Returns:
        An NxN numpy array with values in {0, 2, 3, 5}.
    """
    if len(row_seed) != N or len(col_seed) != N:
        raise ValueError("row_seed and col_seed must each have length N.")

    # Must be integer arrays: ~0 = -1, -1+2 = 1; ~1 = -2, -2+2 = 0
    row_seed = row_seed.astype(int) & 1
    col_seed = col_seed.astype(int) & 1

    # Horizontal borders (value 2): even columns follow row_seed,
    # odd columns follow its complement.
    h = np.ones((N, N), dtype=int)
    h[:, ::2]  = (h[:, ::2].T  * 2 * row_seed).T
    h[:, 1::2] = (h[:, 1::2].T * 2 * (~row_seed + 2)).T

    # Vertical borders (value 3): even rows follow col_seed,
    # odd rows follow its complement.
    v = np.ones((N, N), dtype=int)
    v[::2]  = v[::2]  * 3 * col_seed
    v[1::2] = v[1::2] * 3 * (~col_seed + 2)

    return h + v


def random_textile(N: int, p: float = 0.5, seed: int | None = None) -> np.ndarray:
    """Generate an NxN textile from random binary seeds.

    Args:
        N:    Size of the grid.
        p:    Probability of a 1 in each seed position (default 0.5).
        seed: Optional random seed for reproducibility.

    Returns:
        An NxN numpy array with values in {0, 2, 3, 5}.
    """
    rng = np.random.default_rng(seed)
    row_seed = rng.binomial(1, p, N).astype(bool)
    col_seed = rng.binomial(1, p, N).astype(bool)
    return generate_textile(N, row_seed, col_seed)


def symmetric_textile(N: int, p: float = 0.5, seed: int | None = None) -> np.ndarray:
    """Generate a textile where row_seed == col_seed, producing diagonal symmetry.

    Args:
        N:    Size of the grid.
        p:    Probability of a 1 in each seed position (default 0.5).
        seed: Optional random seed for reproducibility.

    Returns:
        An NxN numpy array with values in {0, 2, 3, 5}.
    """
    rng = np.random.default_rng(seed)
    shared_seed = rng.binomial(1, p, N).astype(bool)
    return generate_textile(N, shared_seed, shared_seed)
