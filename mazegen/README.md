# mazegen

Reusable maze generator written in Python 3.10+, with no external
dependencies. It builds random but reproducible mazes in two modes:

- **Perfect**: exactly one path between any two cells (no loops).
- **Non-perfect (Pac-Man board)**: every cell reachable, at least two
  independent loops, no 3x3 open area and no dead ends outside the "42".

Every maze big enough (9x7 cells or more) contains a "42" drawn with fully
closed cells.

## Installation

```
pip install mazegen-0.1.0-py3-none-any.whl
```

## Basic example

```python
from mazegen import MazeGenerator, shortest_path

maze = MazeGenerator(width=20, height=15, entry=(0, 0), exit=(19, 14),
                     seed=42)
maze.generate()

path = shortest_path(maze.grid, maze.entry, maze.exit)
print(path)
```

`path` is a string of moves such as `"EESSWS..."`, one letter (`N`, `E`,
`S`, `W`) per step from the entry to the exit.

## Parameters

```python
MazeGenerator(width, height, entry, exit,
              perfect=True, seed=None, algorithm="backtracker")
```

| Parameter | Type | Default | Description |
|:--|:--|:--|:--|
| `width` | `int` | required | Number of columns, greater than 0. |
| `height` | `int` | required | Number of rows, greater than 0. |
| `entry` | `tuple[int, int]` | required | Entry cell as `(x, y)`. |
| `exit` | `tuple[int, int]` | required | Exit cell as `(x, y)`, different from the entry. |
| `perfect` | `bool` | `True` | `True` for a perfect maze, `False` for a Pac-Man board (needs at least 3x3 cells). |
| `seed` | `int` or `None` | `None` | Random seed. The same seed always builds the same maze. With `None`, a random seed is picked and stored in `maze.seed`. |
| `algorithm` | `str` | `"backtracker"` | `"backtracker"` (randomised depth-first search) or `"kruskal"` (randomised Kruskal with union-find). |

Coordinates are `(x, y)`: `x` is the column and `y` the row, starting at
`(0, 0)` in the top-left corner.

Invalid parameters raise `mazegen.MazeGeneratorError` (a subclass of
`ValueError`) with a clear message: size not positive, entry or exit out of
bounds, equal, or inside the "42", Pac-Man board smaller than 3x3, or
unknown algorithm.

```python
from mazegen import MazeGenerator, MazeGeneratorError

try:
    MazeGenerator(width=20, height=15, entry=(0, 0), exit=(0, 0))
except MazeGeneratorError as error:
    print(f"Invalid maze: {error}")
```

## Methods

| Method | Description |
|:--|:--|
| `generate()` | Build the maze with the current seed. Call it before reading `grid`. |
| `regenerate()` | Pick a new random seed and build a new maze. |

## Accessing the generated maze

| Attribute | Description |
|:--|:--|
| `grid` | `list[list[int]]`, read as `grid[y][x]`. Each value from 0 to 15 says which walls of the cell are closed. |
| `pattern_cells` | `set[tuple[int, int]]` with the cells of the "42". Empty if the maze is too small for it. |
| `steps` | `list[tuple[tuple[int, int], int]]` with every wall opened during the generation, in order, as `((x, y), direction)`. Replaying them on a fully closed grid rebuilds `grid`, which is useful for animations. |
| `seed` | Seed used by the last generation. |
| `width`, `height`, `entry`, `exit`, `perfect`, `algorithm` | The parameters given to the constructor. |

### Wall bits

A bit set to 1 means the wall is closed.

| Constant | Value | Wall |
|:--|:--|:--|
| `NORTH` | 1 | top |
| `EAST` | 2 | right |
| `SOUTH` | 4 | bottom |
| `WEST` | 8 | left |

```python
from mazegen import EAST, NORTH, SOUTH, WEST

walls = maze.grid[0][0]
if walls & EAST:
    print("The east wall of (0, 0) is closed.")
```

Neighbouring cells always agree: if a cell has its east wall closed, the
cell to its right has its west wall closed.

## Solution

```python
shortest_path(grid, entry, exit) -> str
```

Returns the shortest path from `entry` to `exit` as `N`, `E`, `S` and `W`
letters, found with a breadth-first search. It raises `ValueError` if there
is no path. Call it after `generate()`.

## License

MIT. See `LICENSE.md`.
