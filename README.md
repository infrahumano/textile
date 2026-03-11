# textile

Generate and explore grid-based **textile** patterns from binary seeds.

A *textile* is a grid pattern produced by two binary sequences — one for rows, one for columns. Each sequence determines where line segments are drawn, and their combination produces surprisingly rich visual structure: distinct enclosed regions, diagonal symmetry, and emergent texture.

This project provides tools to:

- **Generate** textile matrices from binary seeds
- **Analyze** their region structure (connected components via BFS)
- **Visualize** and color the resulting patterns

## Background

Inspired by a series of posts by [@infrahumano](https://infrahumano.github.io/exterior/), exploring a pattern originally shared by [@anniek_p](https://twitter.com/anniek_p/status/1244220881347502080), and further developed with coloring ideas from [@zubie7a](https://twitter.com/zubie7a) and [@moebio](https://twitter.com/moebio).

## Usage

```python
import numpy as np
from textile import generate_textile, determine_regions

N = 80
rng = np.random.default_rng(seed=335)
row_seed = rng.integers(0, 2, N)
col_seed = rng.integers(0, 2, N)

matrix = generate_textile(N, row_seed, col_seed)
regions = determine_regions(matrix)
print(f"Number of regions: {int(regions.max())}")
```

## Installation

```bash
uv sync
```

## License

MIT
