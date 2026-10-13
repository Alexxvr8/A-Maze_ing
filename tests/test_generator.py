"""test_generator.py: checks for the maze generator."""


from collections import deque

import pytest

from mazegen import EAST, NORTH, SOUTH, WEST
from mazegen import MazeGenerator, MazeGeneratorError
from mazegen.directions import ALL_DIRECTIONS, ALL_WALLS, DELTAS, OPPOSITE


SEEDS = [0, 1, 42, 1234, 99999]
SMALL_SIZES = [(8, 15), (20, 6), (5, 5)]
INVALID_PARAMS = [
    (0, 15, (0, 0), (1, 1)),
    (20, -1, (0, 0), (1, 1)),
    (20, 15, (20, 0), (19, 14)),
    (20, 15, (-1, 0), (19, 14)),
    (20, 15, (0, 0), (0, 15)),
    (20, 15, (3, 3), (3, 3)),
    (20, 15, (6, 5), (19, 14)),
    (20, 15, (0, 0), (6, 5)),
]


def _build(seed: int, width: int = 20, height: int = 15) -> MazeGenerator:
    """Create and generate a maze with fixed entry and exit corners."""
    maze = MazeGenerator(
        width=width,
        height=height,
        entry=(0, 0),
        exit=(width - 1, height - 1),
        seed=seed,
    )
    maze.generate()
    return maze


def _reachable(maze: MazeGenerator) -> set[tuple[int, int]]:
    """Return every cell that can be reached from the entry."""
    visited: set[tuple[int, int]] = {maze.entry}
    queue: deque[tuple[int, int]] = deque([maze.entry])
    grid = maze.grid

    while queue:
        x, y = queue.popleft()

        for direction in ALL_DIRECTIONS:
            if grid[y][x] & direction:
                continue

            dx, dy = DELTAS[direction]
            neighbour = (x + dx, y + dy)
            if neighbour not in visited:
                visited.add(neighbour)
                queue.append(neighbour)

    return visited


@pytest.mark.parametrize("seed", SEEDS)
def test_border_is_closed(seed: int) -> None:
    """Every cell on the outer border has its outer wall closed."""
    maze = _build(seed)
    grid = maze.grid
    width = maze.width
    height = maze.height

    for x in range(width):
        assert grid[0][x] & NORTH
        assert grid[height - 1][x] & SOUTH

    for y in range(height):
        assert grid[y][0] & WEST
        assert grid[y][width - 1] & EAST


@pytest.mark.parametrize("seed", SEEDS)
def test_walls_are_coherent(seed: int) -> None:
    """Two neighbour cells always agree on the wall between them."""
    maze = _build(seed)
    grid = maze.grid
    width = maze.width
    height = maze.height

    for y in range(height):
        for x in range(width):
            for direction in ALL_DIRECTIONS:
                dx, dy = DELTAS[direction]
                nx = x + dx
                ny = y + dy
                if not (0 <= nx < width and 0 <= ny < height):
                    continue

                cell_wall = bool(grid[y][x] & direction)
                neighbour_wall = bool(grid[ny][nx] & OPPOSITE[direction])
                assert cell_wall == neighbour_wall


@pytest.mark.parametrize("seed", SEEDS)
def test_pattern_cells_are_closed(seed: int) -> None:
    """Every cell of the "42" pattern has all four walls closed."""
    maze = _build(seed)
    pattern_cells = maze.pattern_cells

    assert pattern_cells
    for x, y in pattern_cells:
        assert maze.grid[y][x] == ALL_WALLS


@pytest.mark.parametrize("seed", SEEDS)
def test_all_cells_reachable(seed: int) -> None:
    """Every cell outside the "42" can be reached from the entry."""
    maze = _build(seed)
    reached = _reachable(maze)
    expected = maze.width * maze.height - len(maze.pattern_cells)

    assert len(reached) == expected
    assert maze.exit in reached


@pytest.mark.parametrize("seed", SEEDS)
def test_maze_is_perfect(seed: int) -> None:
    """A perfect maze has exactly one path between any two cells."""
    maze = _build(seed)
    grid = maze.grid
    reached = _reachable(maze)

    passages = 0
    for y in range(maze.height):
        for x in range(maze.width):
            if not (grid[y][x] & EAST):
                passages += 1
            if not (grid[y][x] & SOUTH):
                passages += 1

    assert passages == len(reached) - 1


@pytest.mark.parametrize("seed", SEEDS)
def test_same_seed_same_maze(seed: int) -> None:
    """The same seed always builds the same maze."""
    first = _build(seed)
    second = _build(seed)
    other = _build(seed + 1)

    assert first.grid == second.grid
    assert first.grid != other.grid


@pytest.mark.parametrize("width, height", SMALL_SIZES)
def test_small_maze_has_no_pattern(width: int, height: int) -> None:
    """A maze too small for the "42" is generated without it."""
    maze = _build(42, width, height)
    reached = _reachable(maze)

    assert maze.pattern_cells == set()
    assert len(reached) == width * height


@pytest.mark.parametrize("width, height, entry, exit_", INVALID_PARAMS)
def test_invalid_params_raise(
    width: int,
    height: int,
    entry: tuple[int, int],
    exit_: tuple[int, int],
) -> None:
    """Invalid sizes or entry/exit cells raise MazeGeneratorError."""
    with pytest.raises(MazeGeneratorError):
        MazeGenerator(width=width, height=height, entry=entry, exit=exit_)
