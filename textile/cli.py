"""
Command-line interface for the textile project.

Usage examples:
    textile                             # 80x80 random, auto-named PNG
    textile -n 200                      # 200x200 random
    textile -n 100 -o my_textile.png    # custom output file
    textile -n 100 --seed 42            # reproducible result
    textile -n 100 --symmetric          # diagonal-symmetric pattern
    textile -n 100 --mode side-by-side
    textile -n 100 -o pattern.oxs       # export as OXS cross-stitch file
    textile -n 100 --format oxs         # same, with auto-named .oxs file
"""

import argparse
from datetime import datetime
from pathlib import Path

from .core import random_textile, symmetric_textile
from .regions import determine_regions, region_count
from .viz import plot_regions, plot_borders, plot_side_by_side
from .export import save_oxs


def _auto_filename(
    n: int,
    seed: int | None,
    symmetric: bool,
    fmt: str,
    mode: str,
    colouring: str,
) -> str:
    """Generate a descriptive filename when none is provided."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    kind = "sym" if symmetric else "rnd"
    seed_tag = f"_s{seed}" if seed is not None else ""
    if fmt == "oxs":
        return f"textile_{n}x{n}_{kind}{seed_tag}_{ts}.oxs"
    colouring_tag = f"_{colouring}" if mode != "borders" else ""
    return f"textile_{n}x{n}_{kind}{seed_tag}_{mode}{colouring_tag}_{ts}.png"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="textile",
        description="Generate grid-based textile patterns from binary seeds.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  textile                               80x80 random textile, auto-named PNG
  textile -n 200                        200x200 random textile
  textile -n 100 -o out.png             custom output file name
  textile -n 100 --seed 42              reproducible pattern
  textile -n 100 --symmetric            diagonal-symmetric pattern
  textile -n 100 --mode borders         draw border lines instead of filled regions
  textile -n 100 --mode side-by-side    both views side by side
  textile -n 100 --colouring random     one unique colour per region (blog style)
  textile -n 100 --colouring greedy     minimal colours, no adjacent regions share one
  textile -n 100 -o pattern.oxs         export as OXS cross-stitch file
  textile -n 100 --format oxs           same, with auto-named .oxs file
  textile -n 100 --format oxs --no-borders  export without border back stitches
        """,
    )

    parser.add_argument(
        "-n", "--size",
        type=int,
        default=80,
        metavar="N",
        help="grid size (NxN), default: 80",
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        metavar="FILE",
        help="output file path — use a .oxs extension to export cross-stitch format",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="SEED",
        help="random seed for reproducibility",
    )
    parser.add_argument(
        "--symmetric",
        action="store_true",
        help="use the same seed for rows and columns (produces diagonal symmetry)",
    )
    parser.add_argument(
        "--format",
        choices=["png", "oxs"],
        default=None,
        metavar="FORMAT",
        help=(
            "output format: 'png' (default) or 'oxs' (Open Cross-Stitch XML). "
            "Inferred automatically from the -o extension when provided."
        ),
    )
    parser.add_argument(
        "--mode",
        choices=["regions", "borders", "side-by-side"],
        default="regions",
        help="PNG visualization mode (default: regions); ignored for OXS export",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=150,
        metavar="DPI",
        help="PNG resolution in DPI (default: 150); ignored for OXS export",
    )
    parser.add_argument(
        "--colouring",
        choices=["greedy", "random"],
        default="greedy",
        help=(
            "colouring strategy for regions (default: greedy). "
            "'greedy' uses minimal colours so no adjacent regions share one "
            "(typically 4, per the four-colour theorem). "
            "'random' gives every region its own unique colour — "
            "the approach from the original infrahumano blog posts."
        ),
    )
    parser.add_argument(
        "--no-borders",
        action="store_true",
        help="OXS only: omit back stitches for border lines (export fills only)",
    )
    parser.add_argument(
        "--border-color",
        type=str,
        default="1C1C1C",
        metavar="RRGGBB",
        help="OXS only: hex RGB colour for border back stitches (default: 1C1C1C)",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.size < 2:
        parser.error("--size must be at least 2")

    # Resolve output format: explicit --format wins, else infer from extension
    fmt = args.format
    if fmt is None:
        if args.output and args.output.lower().endswith(".oxs"):
            fmt = "oxs"
        else:
            fmt = "png"

    # Generate the textile matrix
    gen = symmetric_textile if args.symmetric else random_textile
    matrix = gen(args.size, seed=args.seed)

    regions = determine_regions(matrix)
    n_regions = region_count(regions)
    kind = "symmetric" if args.symmetric else "random"
    seed_info = f"seed={args.seed}" if args.seed is not None else "no seed"

    # Determine output path
    output = args.output or _auto_filename(
        args.size, args.seed, args.symmetric, fmt, args.mode, args.colouring
    )
    output_path = Path(output)

    # ------------------------------------------------------------------ #
    # Export                                                               #
    # ------------------------------------------------------------------ #
    if fmt == "oxs":
        save_oxs(
            matrix,
            output_path,
            colouring=args.colouring,
            color_seed=args.seed,
            title=f"Textile {args.size}x{args.size}",
            borders=not args.no_borders,
            border_color=args.border_color,
        )
        print(f"{kind} {args.size}x{args.size} textile ({seed_info})")
        print(f"  regions : {n_regions}")
        print(f"  borders : {'yes' if not args.no_borders else 'no'}")
        print(f"  saved   : {output_path}")

    else:  # png
        mode = args.mode.replace("-", "_")  # "side-by-side" → "side_by_side"
        n_colours = None
        if mode == "regions":
            fig, n_colours = plot_regions(
                matrix, color_seed=args.seed, colouring=args.colouring
            )
        elif mode == "borders":
            fig = plot_borders(matrix)
        else:  # side_by_side
            fig, n_colours = plot_side_by_side(
                matrix, color_seed=args.seed, colouring=args.colouring
            )
        fig.savefig(output_path, dpi=args.dpi, bbox_inches="tight")

        print(f"{kind} {args.size}x{args.size} textile ({seed_info})")
        print(f"  regions : {n_regions}")
        if n_colours is not None:
            print(f"  colours : {n_colours} ({args.colouring})")
        print(f"  saved   : {output_path}")


if __name__ == "__main__":
    main()
