*This project has been created as part of the 42 curriculum by alvicent, joserome.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generator written in Python. It reads a configuration
file, generates a random but reproducible maze, writes it to a file using a
hexadecimal wall encoding, and displays it in a window (MiniLibX) where the
user can regenerate the maze, show or hide the shortest path and change the
wall colours.

The maze always contains a visible "42" pattern made of fully closed cells.
It can be generated in two modes:

- **Perfect**: exactly one path between any two cells.
- **Non-perfect (Pac-Man style)**: loops and very few dead ends.

The generation logic lives in a standalone, installable package called
`mazegen`, so it can be reused in other projects.

## Instructions

### Requirements

- Python 3.10 or later
- [Poetry](https://python-poetry.org/)
- TODO: MiniLibX requirements

### Installation

```
make install
```

This creates a virtual environment in `.venv/` and installs the development
tools (flake8, mypy, build, pytest) with the exact versions in
`poetry.lock`.

### Usage

```
make run                          # uses config.txt
make run CONFIG=path/to/file.txt  # uses another config file
```

or directly:

```
poetry run python a_maze_ing.py config.txt
```

### Other Makefile rules

| Rule | Description |
|:--|:--|
| `make debug` | Run the program under `pdb` |
| `make lint` | Run flake8 and mypy with the required flags |
| `make lint-strict` | Run flake8 and `mypy --strict` |
| `make clean` | Remove caches and build artefacts |

## Configuration file

One `KEY=VALUE` pair per line. Lines starting with `#` are ignored.

| Key | Required | Description | Example |
|:--|:--|:--|:--|
| `WIDTH` | yes | Number of columns | `WIDTH=20` |
| `HEIGHT` | yes | Number of rows | `HEIGHT=15` |
| `ENTRY` | yes | Entry cell, as `x,y` | `ENTRY=0,0` |
| `EXIT` | yes | Exit cell, as `x,y` | `EXIT=19,14` |
| `OUTPUT_FILE` | yes | Output file name | `OUTPUT_FILE=maze.txt` |
| `PERFECT` | yes | `true`/`yes`/`1` or `false`/`no`/`0` (case-insensitive) | `PERFECT=True` |
| `SEED` | no | Integer seed. If missing, a random one is used and printed | `SEED=42` |

Coordinates use `x` for the column and `y` for the row, starting at `0,0` in
the top-left corner.

The program stops with a clear error message (never a traceback) when:

- the file does not exist or cannot be read;
- a required key is missing, duplicated or unknown;
- a value has the wrong format;
- `ENTRY` or `EXIT` are out of bounds, equal, or inside the "42" pattern.

## Maze generation algorithm

**Perfect mode** uses the **recursive backtracker** (randomised depth-first
search), implemented with an explicit stack instead of recursion.

**Why this algorithm:** TODO

**Non-perfect mode:** TODO

## Reusable code

TODO: how to build, install and use the `mazegen` package.

## Team and project management

### Roles

| Member | Role |
|:--|:--|
| alvicent | TODO |
| `<login2>` | TODO |

### Planning

TODO: anticipated planning and how it evolved.

### What worked well and what could be improved

TODO

### Tools

Git and GitHub (branches and pull requests), Poetry, flake8, mypy, pytest,
pdb, MiniLibX.

## Resources

- TODO: references on maze generation, BFS, Python packaging

### Use of AI

TODO: which tasks and which parts of the project.

## License

This project is released under the MIT License. See `LICENSE.md`.