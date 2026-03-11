"""
OXS export for textile patterns.

Converts a textile matrix into an Open Cross-Stitch (OXS) XML file that can
be loaded by cross-stitch software such as WinStitch, MacStitch, or Embroiderly.

Mapping from textile to cross-stitch:
  - Every grid cell becomes a **full stitch** coloured by its region.
  - Every border edge (values 2, 3, 5 in the matrix) becomes a **back stitch**
    drawn along that cell edge, forming the visible line pattern of the textile.

Coordinate conventions (OXS):
  - Full stitch at cell (row r, col c): x=c, y=r  (0-indexed integers).
  - Back stitch along the *right* edge of cell (r, c): x1=c+1, y1=r,  x2=c+1, y2=r+1.
  - Back stitch along the *bottom* edge of cell (r, c): x1=c,  y1=r+1, x2=c+1, y2=r+1.
"""

from __future__ import annotations

from pathlib import Path
from xml.dom import minidom
import xml.etree.ElementTree as ET

import numpy as np

from .regions import determine_regions, region_count
from .colouring import (
    build_adjacency,
    greedy_colouring,
    random_colouring,
    colour_count,
    make_colour_palette,
)


def _rgba_to_hex(rgba: np.ndarray) -> str:
    """Convert a float RGBA row (values in [0, 1]) to a hex RGB string ``RRGGBB``."""
    r, g, b = (int(round(x * 255)) for x in rgba[:3])
    return f"{r:02X}{g:02X}{b:02X}"


def to_oxs(
    matrix: np.ndarray,
    colouring: str = "greedy",
    color_seed: int | None = None,
    title: str = "Textile",
    borders: bool = True,
    border_color: str = "1C1C1C",
) -> str:
    """Convert a textile matrix to an OXS cross-stitch pattern string.

    Args:
        matrix:       The textile matrix (values in {0, 2, 3, 5}).
        colouring:    Region colouring strategy: ``"greedy"`` or ``"random"``.
        color_seed:   Optional seed for reproducible region colours.
        title:        Pattern title written into the OXS properties.
        borders:      If ``True`` (default), add back stitches along every
                      border edge in the matrix, reproducing the textile line
                      pattern.  If ``False``, only filled regions are exported.
        border_color: Hex RGB colour (``RRGGBB``) for the border back stitches.
                      Defaults to near-black ``"1C1C1C"``.

    Returns:
        A pretty-printed OXS XML string (UTF-8, includes declaration).
    """
    if colouring not in ("greedy", "random"):
        raise ValueError(f"colouring must be 'greedy' or 'random', got {colouring!r}")

    N = matrix.shape[0]
    region_matrix = determine_regions(matrix)
    n_regions = region_count(region_matrix)

    # Build colour map: region index → 0-based colour index
    if colouring == "greedy":
        adjacency = build_adjacency(region_matrix)
        colour_map = greedy_colouring(adjacency, n_regions)
    else:
        colour_map = random_colouring(n_regions)
    n_colours = colour_count(colour_map)

    # RGBA palette for region fills
    palette_rgba = make_colour_palette(n_colours, seed=color_seed)

    # Palette index layout:
    #   0              → cloth / fabric (white background)
    #   1 .. n_colours → region fill colours
    #   n_colours + 1  → border line colour (only added when borders=True)
    border_palindex = n_colours + 1

    # ------------------------------------------------------------------ #
    # Build XML tree                                                       #
    # ------------------------------------------------------------------ #
    root = ET.Element("chart")

    ET.SubElement(
        root, "properties",
        oxsversion="1.0",
        software="textile",
        chartheight=str(N),
        chartwidth=str(N),
        charttitle=title,
        palettecount=str(n_colours + (1 if borders else 0)),
    )

    # --- palette ---
    palette_el = ET.SubElement(root, "palette")

    ET.SubElement(palette_el, "palette_item",
        index="0",
        number="cloth",
        name="cloth",
        color="FFFFFF",
        printcolor="FFFFFF",
        blendcolor="nil",
        strands="2",
        bsstrands="2",
        bscolor="FFFFFF",
    )
    for i, rgba in enumerate(palette_rgba):
        hex_color = _rgba_to_hex(rgba)
        ET.SubElement(palette_el, "palette_item",
            index=str(i + 1),
            number=f"Custom {i + 1}",
            name=f"Colour {i + 1}",
            color=hex_color,
            printcolor=hex_color,
            blendcolor="nil",
            strands="2",
            bsstrands="2",
            bscolor=hex_color,
        )
    if borders:
        ET.SubElement(palette_el, "palette_item",
            index=str(border_palindex),
            number="Border",
            name="Border",
            color=border_color.upper(),
            printcolor=border_color.upper(),
            blendcolor="nil",
            strands="1",
            bsstrands="1",
            bscolor=border_color.upper(),
        )

    # --- full stitches ---
    fullstitches_el = ET.SubElement(root, "fullstitches")
    for r in range(N):
        for c in range(N):
            region = int(region_matrix[r, c])
            pal_idx = colour_map[region] + 1  # shift to 1-based palette index
            ET.SubElement(fullstitches_el, "stitch",
                x=str(c),
                y=str(r),
                palindex=str(pal_idx),
            )

    # --- back stitches (border lines) ---
    backstitches_el = ET.SubElement(root, "backstitches")
    if borders:
        bpi = str(border_palindex)
        for r in range(N):
            for c in range(N):
                val = int(matrix[r, c])
                # Right border (val 2 or 5): vertical segment at x = c+1
                if val in (2, 5):
                    ET.SubElement(backstitches_el, "backstitch",
                        x1=str(c + 1), y1=str(r),
                        x2=str(c + 1), y2=str(r + 1),
                        palindex=bpi,
                        objecttype="backstitch",
                    )
                # Bottom border (val 3 or 5): horizontal segment at y = r+1
                if val in (3, 5):
                    ET.SubElement(backstitches_el, "backstitch",
                        x1=str(c), y1=str(r + 1),
                        x2=str(c + 1), y2=str(r + 1),
                        palindex=bpi,
                        objecttype="backstitch",
                    )

    # --- pretty-print ---
    raw = ET.tostring(root, encoding="unicode")
    dom = minidom.parseString(raw)
    return dom.toprettyxml(indent="  ", encoding=None)


def save_oxs(
    matrix: np.ndarray,
    path: str | Path,
    **kwargs,
) -> None:
    """Save a textile matrix as an OXS cross-stitch pattern file.

    All keyword arguments are forwarded to :func:`to_oxs`.

    Args:
        matrix: The textile matrix (values in {0, 2, 3, 5}).
        path:   Destination file path (typically ending in ``.oxs``).
    """
    xml_str = to_oxs(matrix, **kwargs)
    Path(path).write_text(xml_str, encoding="utf-8")
