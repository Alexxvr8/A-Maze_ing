*This project has been created as part of the 42 curriculum by alvicent, joserome.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python. You give it a small text
file with a few settings, and it:

1. generates a random maze (the same seed always gives the same maze);
2. writes it to a file, with one hexadecimal digit per cell;
3. opens a window where you can watch it, regenerate it, show the shortest
   path and change the colours.

Every maze big enough contains a visible **"42"** drawn with fully closed
cells. The maze can be generated in two modes:

- **Perfect** (`PERFECT=True`): there is exactly one path between any two
  cells, so there are no loops at all.
- **Pac-Man board** (`PERFECT=False`): every corridor is reachable, the four
  corners and the centre are open, there are at least two independent
  loops so a chased player always has another way out, and the dead ends
  are removed.

The generation logic lives in its own installable package, `mazegen`, so it
can be reused in other projects (see [Reusable code](#reusable-code)).

### Features

- Two generation algorithms: **recursive backtracker** and **Kruskal**.
- Pac-Man mode with its dead ends removed ("braided" board).
- Animated generation: watch the walls open one by one.
- Shortest path, shown and hidden from the window, also animated.
- Five wall colours, plus fixed colours for the entry, the exit and the
  "42".

## Instructions

### Requirements

- Python 3.10 or later
- [Poetry](https://python-poetry.org/)
- Linux with a graphical session (X11), for the window
- The XCB keysyms library, needed by MiniLibX. On Ubuntu:

  ```
  sudo apt install libxcb-keysyms1
  ```

MiniLibX itself does not need a separate installation: its Python wheel is
included in `vendor/` and installed by `make install`.

### Installation

```
make install
```

This creates a virtual environment in `.venv/` and installs everything with
the exact versions written in `poetry.lock`: MiniLibX and the development
tools (flake8, mypy, pytest, build).

### Usage

```
make run                          # uses config.txt
make run CONFIG=path/to/file.txt  # uses another config file
```

or directly:

```
poetry run python a_maze_ing.py config.txt
```

The program writes the maze to the output file and then opens the window.

### Controls

| Key | Action |
|:--|:--|
| `R` | Generate a new maze (animated) |
| `P` | Show or hide the shortest path (animated) |
| `C` | Change the wall colour |
| `A` | Replay the generation animation |
| `ESC` or the window cross | Quit |

Colours: the entry is green, the exit is red, the path is yellow and the
"42" is grey.

### Other Makefile rules

| Rule | Description |
|:--|:--|
| `make debug` | Run the program under `pdb` |
| `make lint` | Run flake8 and mypy with the flags required by the subject |
| `make lint-strict` | Run flake8 and `mypy --strict` |
| `make test` | Run the test suite with pytest |
| `make clean` | Remove caches and build artefacts |

## Configuration file

The configuration file has one `KEY=VALUE` pair per line. Empty lines and
lines starting with `#` are ignored. This is the default `config.txt`:

```
# A-Maze-ing default configuration
# Coordinates are x,y (column,row), starting at 0,0 in the top-left corner.
# Optional: SEED=<integer> to reproduce a maze (random if missing).

WIDTH=20
HEIGHT=15
ENTRY=0,0
EXIT=19,14
OUTPUT_FILE=maze.txt
PERFECT=True
```

| Key | Required | Description | Example |
|:--|:--|:--|:--|
| `WIDTH` | yes | Number of columns | `WIDTH=20` |
| `HEIGHT` | yes | Number of rows | `HEIGHT=15` |
| `ENTRY` | yes | Entry cell, as `x,y` | `ENTRY=0,0` |
| `EXIT` | yes | Exit cell, as `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | yes | File where the maze is written | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | `true`/`yes`/`1` or `false`/`no`/`0`, in any case | `PERFECT=True` |
| `SEED` | no | Integer seed. If missing, a random one is used | `SEED=42` |
| `ALGORITHM` | no | `backtracker` (default) or `kruskal`, in any case | `ALGORITHM=kruskal` |

Coordinates use `x` for the column and `y` for the row, starting at `0,0` in
the top-left corner.

Rules for the values:

- `WIDTH` and `HEIGHT` must be positive.
- `ENTRY` and `EXIT` must be inside the maze, different, and not on a cell
  of the "42".
- The Pac-Man mode needs at least 3x3 cells.
- The "42" needs at least 9x7 cells. In a smaller maze it is left out and a
  message is printed.

The program never crashes with a traceback: it stops with a clear error
message when the file does not exist, a line has no `=`, a key is missing,
duplicated or unknown, a value has the wrong format, or the values above are
not respected. The `configs/` folder contains one example file for each of
these errors.

### Output file

The maze is written row by row, one line per row, with one hexadecimal
digit per cell. Each bit of the digit is a wall, and a bit set to 1 means
the wall is closed:

| Bit | Value | Wall |
|:--|:--|:--|
| 0 | 1 | North |
| 1 | 2 | East |
| 2 | 4 | South |
| 3 | 8 | West |

For example, `9` (`1001`) means the north and west walls are closed, and
`f` means all four walls are closed (the cells of the "42").

After the grid there is an empty line and three more lines: the entry
coordinates, the exit coordinates and the shortest path from the entry to
the exit written with the letters `N`, `E`, `S` and `W`.

## Maze generation algorithms

### Recursive backtracker (default)

A randomised depth-first search. It starts at the entry, moves to a random
neighbour that has not been visited yet and opens the wall between them.
When it gets stuck it goes back until it finds a cell with unvisited
neighbours. We use an explicit stack instead of recursion, so big mazes do
not hit Python's recursion limit.

### Kruskal

Every cell starts as its own group. All the inner walls are shuffled and
visited one by one: a wall is opened only if the two cells on each side
belong to different groups, and then the groups are joined. A wall between
two cells of the same group would create a loop, so it is kept. The groups
are tracked with a **union-find** structure with path halving, which keeps
a 200x200 maze under half a second.

### Why these algorithms

We chose the **recursive backtracker** as the main algorithm because it is
easy to understand and to explain, it always builds a perfect maze (a
spanning tree of the grid), and it produces long winding corridors that
look good on screen. It also deals naturally with the "42": its cells are
simply never visited.

We added **Kruskal** as a second algorithm (bonus) because it works in a
completely different way, joining random pieces instead of walking one long
path. Its mazes have many short dead ends and look very different, which
makes the comparison interesting.

### Pac-Man mode

The Pac-Man board starts from a perfect maze built with the chosen
algorithm, and then:

1. **Braiding:** every dead end gets one extra wall opened. A neighbour that
   is also a dead end is preferred, so one opening can fix two of them.
2. **Loops:** if the maze still has fewer than two independent loops (this
   happens in very small mazes), extra walls are opened until it has two.
3. **No open areas:** every opening is checked, and it is undone if it
   would create a fully open 3x3 area.

The number of loops is counted with a simple formula: a connected maze with
no loops has exactly one passage fewer than cells, so every extra passage
is one loop.

### The "42"

The "42" is a fixed pattern of 7x5 cells, centred in the maze with at least
one free cell around it. Its cells keep their four walls closed, and the
algorithms never enter them.

### Reproducibility

All the random choices of one generation come from a single
`random.Random(seed)` object. The same seed, size and options always give
exactly the same maze.

## Reusable code

The whole generator is the `mazegen` package. It has no dependencies and
knows nothing about the configuration file or the window, so it can be
reused as it is in another project.

| Reusable (`mazegen/`) | Specific to this project (`app/`, `a_maze_ing.py`) |
|:--|:--|
| `MazeGenerator` class: validation, both algorithms, Pac-Man mode, animation steps | Configuration file parser |
| `shortest_path` function | Output file writer |
| Wall constants `NORTH`, `EAST`, `SOUTH`, `WEST` | MiniLibX window and controls |

It is packaged as `mazegen-0.1.0-py3-none-any.whl`, at the root of this
repository. To install it in another project:

```
pip install mazegen-0.1.0-py3-none-any.whl
```

Basic example:

```python
from mazegen import MazeGenerator, shortest_path

maze = MazeGenerator(width=20, height=15, entry=(0, 0), exit=(19, 14),
                     perfect=False, seed=42, algorithm="kruskal")
maze.generate()

print(maze.grid[0][0])
print(shortest_path(maze.grid, maze.entry, maze.exit))
```

- **Custom parameters:** `width`, `height`, `entry`, `exit`, `perfect`,
  `seed` and `algorithm`, all passed to the constructor.
- **The structure:** `maze.grid[y][x]` is a number from 0 to 15 with the
  closed walls of each cell, `maze.pattern_cells` holds the cells of the
  "42" and `maze.steps` the walls opened in order.
- **A solution:** `shortest_path` returns the moves from the entry to the
  exit as `N`, `E`, `S` and `W` letters.

The full documentation of the package is in
[`mazegen/README.md`](mazegen/README.md), and it is also included inside the
wheel.

To build the package again from the sources:

```
python3 -m venv venv
source venv/bin/activate
pip install build
python -m build
```

The `.whl` and `.tar.gz` files appear in `dist/`.

## Team and project management

### Roles

We split the project into two lines of work with a clear contract between
them, written in `NOTES.md` before writing any code:

| Member | Line | Main work |
|:--|:--|:--|
| **alvicent** | A: the engine | The `mazegen` generator: validation, the "42", recursive backtracker, Kruskal, Pac-Man mode, animation steps and the engine tests. Also the MiniLibX installation, the license, the packaging and the documentation. |
| **joserome** | B: everything that uses the engine | The configuration parser and its test files, the solver, the output writer, the MiniLibX window with its controls and the animation, and the main program `a_maze_ing.py`. |

Both of us review each other's work and must be able to explain every part
of the project.

### Planning

We planned the work in phases, with a few checkpoints where the two lines
had to meet:

| Phase | Planned goal | Done |
|:--|:--|:--|
| 0. Agreements and setup | Repository, tools, contract, coding style | 2026-10-09 |
| 1. Minimal core | Generator, parser, solver, writer and tests | 2026-10-13 |
| 2. Pac-Man mode | Braiding, at least two loops, no 3x3 areas | 2026-10-16 |
| 3. Display | MiniLibX window with the controls | 2026-10-16 |
| 4. Bonuses | Kruskal, no dead ends, animation | 2026-10-16 to 2026-10-18 |
| 5. Integration | `a_maze_ing.py` joining all the parts | 2026-10-20 |
| 6. Packaging and delivery | MiniLibX install, license, wheel, README | 2026-10-20 |

How it evolved: the first phases went as planned, and we ended up doing all
three bonuses. The main change was the integration: we planned to write
`a_maze_ing.py` right after the core, but we kept improving each line on
its own and left it for the end.

### What worked well and what could be improved

**What worked well:** almost everything. We agreed on the contract between
the two lines in `NOTES.md` (the grid format, the coordinates, the errors,
who checks what) before writing code, so each of us could work on his own
part without blocking the other. We only stepped on each other once, about
whether the parser or the generator should check the values, and we solved
it by writing the rule down: the parser checks the format, and the
generator checks the values. Working side by side and reviewing every pull
request together also helped a lot.

**What could be improved:** we should have written `a_maze_ing.py` much
earlier. Until then, every test of the whole program had to be done with
small terminal commands instead of simply running the program.

### Tools

- Git and GitHub, with one branch and one pull request per change
- VS Code
- Poetry for the virtual environment and the dependencies
- flake8, mypy and pytest
- `build` for the package and `pdb` for debugging
- MiniLibX for the window
- `maze_analyzer.py` (provided with the subject) to check the generated
  mazes
- `NOTES.md` to keep the decisions, the contract and the planning

## Resources

- [Maze generation algorithm](https://en.wikipedia.org/wiki/Maze_generation_algorithm) (Wikipedia): overview of the classic algorithms.
- [Kruskal's algorithm](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm) and [Disjoint-set data structure](https://en.wikipedia.org/wiki/Disjoint-set_data_structure) (Wikipedia): the base of our second algorithm.
- [Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search) (Wikipedia): used to find the shortest path.
- [Mazes for Programmers](https://www.oreilly.com/library/view/mazes-for-programmers/9781680501315/f_0066.html), Jamis Buck: the chapter on braiding mazes.
- [Python Packaging User Guide](https://packaging.python.org/en/latest/tutorials/packaging-projects/): how to build a wheel.
- [Poetry documentation](https://python-poetry.org/docs/)
- [mypy documentation](https://mypy.readthedocs.io/)
- [PEP 257](https://peps.python.org/pep-0257/): docstring conventions.
- [MIT License](https://choosealicense.com/licenses/mit/) at choosealicense.com: why we chose it.

### Use of AI

We used Claude (Anthropic) as a teacher and as a reviewer:

- **Teacher:** it explained the new concepts (union-find, bit masks, BFS,
  braiding, Python packaging) with examples taken from other domains, so we
  could apply the technique ourselves.
- **Reviewer:** it reviewed the code we wrote, pointing out bugs first and
  then style, flake8 and mypy issues.
- **Organisation:** it helped us split the work into the two lines and set
  the goals of each one.
- **Documentation and project files:** it helped us write this
  `README.md`, the package documentation (`mazegen/README.md`), the
  `LICENSE.md` and the `Makefile`.
- **English:** it helped us write and translate our docstrings and
  comments correctly.
- **Early testing:** before `a_maze_ing.py` existed, it helped us write the
  small terminal commands we used to test the program. These commands were
  only used for that early testing and are not part of the project.

## License

This project is released under the MIT License. See
[`LICENSE.md`](LICENSE.md).