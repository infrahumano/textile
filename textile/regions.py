"""
Region detection for textile matrices.

Uses a Breadth-First Search (BFS) flood-fill to identify and label
all connected regions in a textile, respecting the border structure
encoded in the matrix values.

Border encoding:
  - Value 2 means a right border on that cell (blocks rightward travel).
  - Value 3 means a bottom border on that cell (blocks downward travel).
  - Value 5 means both (2 + 3).
"""

import numpy as np
from collections import deque


def _can_move_right(matrix: np.ndarray, row: int, col: int) -> bool:
    """True if there is no right border on the current cell."""
    return matrix[row, col] != 2 and matrix[row, col] != 5


def _can_move_down(matrix: np.ndarray, row: int, col: int) -> bool:
    """True if there is no bottom border on the current cell."""
    return matrix[row, col] != 3 and matrix[row, col] != 5


def bfs(
    matrix: np.ndarray,
    row: int,
    col: int,
    region_matrix: np.ndarray,
    region_index: int,
) -> None:
    """Flood-fill a single region starting from (row, col).

    Travels to unvisited neighbours unless a border blocks the way.
    Modifies region_matrix in place.

    Args:
        matrix:       The textile matrix (values in {0, 2, 3, 5}).
        row:          Starting row.
        col:          Starting column.
        region_matrix: Output matrix being filled with region labels.
        region_index: The label to assign to this region.
    """
    rows, cols = matrix.shape
    queue: deque[tuple[int, int]] = deque([(row, col)])

    while queue:
        r, c = queue.popleft()

        if region_matrix[r, c] != 0:
            continue
        region_matrix[r, c] = region_index

        # Move up: check if the cell above has no bottom border.
        if r > 0 and region_matrix[r - 1, c] == 0:
            if _can_move_down(matrix, r - 1, c):
                queue.append((r - 1, c))

        # Move down: check if the current cell has no bottom border.
        if r + 1 < rows and region_matrix[r + 1, c] == 0:
            if _can_move_down(matrix, r, c):
                queue.append((r + 1, c))

        # Move left: check if the cell to the left has no right border.
        if c > 0 and region_matrix[r, c - 1] == 0:
            if _can_move_right(matrix, r, c - 1):
                queue.append((r, c - 1))

        # Move right: check if the current cell has no right border.
        if c + 1 < cols and region_matrix[r, c + 1] == 0:
            if _can_move_right(matrix, r, c):
                queue.append((r, c + 1))


def determine_regions(matrix: np.ndarray) -> np.ndarray:
    """Label all connected regions in a textile matrix.

    Iterates over every cell; when an unlabelled cell is found, starts
    a new BFS flood-fill from that cell.

    Args:
        matrix: The textile matrix (values in {0, 2, 3, 5}).

    Returns:
        An integer matrix of the same shape, where each cell holds the
        index (1-based) of the region it belongs to.
    """
    region_matrix = np.zeros_like(matrix, dtype=int)
    region_index = 1

    for row in range(matrix.shape[0]):
        for col in range(matrix.shape[1]):
            if region_matrix[row, col] == 0:
                bfs(matrix, row, col, region_matrix, region_index)
                region_index += 1

    return region_matrix


def region_count(region_matrix: np.ndarray) -> int:
    """Return the number of distinct regions in a region matrix.

    Args:
        region_matrix: Output of :func:`determine_regions`.

    Returns:
        The number of regions.
    """
    return int(region_matrix.max())
