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
PATTERN_DEAD_ENDS = 3
SMALL_BRAIDED_SIZES = [(3, 3), (3, 4), (4, 3), (4, 4), (5, 4), (6, 4)]
TOO_SMALL_BRAIDED = [(2, 5), (5, 2), (1, 10)]


def _build(seed: int, width: int = 20, height: int = 15,
           perfect: bool = True) -> MazeGenerator:
    """Create and generate a maze with fixed entry and exit corners."""
    maze = MazeGenerator(
        width=width,
        height=height,
        entry=(0, 0),
        exit=(width - 1, height - 1),
        seed=seed,
        perfect=perfect,
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


def _count_passages(maze: MazeGenerator) -> int:
    """Return how many open walls join two cells of the maze."""
    grid = maze.grid
    passages = 0

    for y in range(maze.height):
        for x in range(maze.width):
            if not (grid[y][x] & EAST):
                passages += 1
            if not (grid[y][x] & SOUTH):
                passages += 1
    return passages


def _count_dead_ends(maze: MazeGenerator) -> int:
    """Return how many cells outside the "42" have exactly one exit."""
    grid = maze.grid
    dead_ends = 0

    for y in range(maze.height):
        for x in range(maze.width):
            if (x, y) in maze.pattern_cells:
                continue
            walls = 0
            for direction in ALL_DIRECTIONS:
                if grid[y][x] & direction:
                    walls += 1
            if walls == 3:
                dead_ends += 1
    return dead_ends


def _has_open_area(maze: MazeGenerator) -> bool:
    """Return whether any 3x3 block of the maze has no inner walls."""
    grid = maze.grid

    for top in range(maze.height - 2):
        for left in range(maze.width - 2):
            walls = 0
            for y in range(top, top + 3):
                for x in range(left, left + 3):
                    if x < left + 2 and grid[y][x] & EAST:
                        walls += 1
                    if y < top + 2 and grid[y][x] & SOUTH:
                        walls += 1

            if walls == 0:
                return True

    return False


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
    reached = _reachable(maze)

    assert _count_passages(maze) == len(reached) - 1


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


@pytest.mark.parametrize("seed", SEEDS)
def test_pacman_all_cells_reachable(seed: int) -> None:
    """Every cell outside the "42" is reachable in the Pac-Man mode."""
    maze = _build(seed=seed, perfect=False)
    reached = _reachable(maze)
    expected = maze.width * maze.height - len(maze.pattern_cells)

    assert len(reached) == expected
    assert maze.exit in reached


@pytest.mark.parametrize("seed", SEEDS)
def test_pacman_has_loops(seed: int) -> None:
    """The Pac-Man mode has at least two independent loops."""
    maze = _build(seed=seed, perfect=False)
    reached = _reachable(maze)

    assert _count_passages(maze) >= (len(reached) - 1) + 2


@pytest.mark.parametrize("seed", SEEDS)
def test_pacman_dead_ends(seed: int) -> None:
    """Only the dead ends forced by the "42" drawing are left."""
    maze = _build(seed=seed, perfect=False)
    no_pattern = _build(seed=seed, width=5, height=5, perfect=False)

    assert _count_dead_ends(maze) <= PATTERN_DEAD_ENDS
    assert _count_dead_ends(no_pattern) == 0


@pytest.mark.parametrize("perfect", [True, False])
@pytest.mark.parametrize("seed", SEEDS)
def test_no_open_area(seed: int, perfect: bool) -> None:
    """No 3x3 block is fully open, in both generation modes."""
    maze = _build(seed, perfect=perfect)
    assert not _has_open_area(maze)


@pytest.mark.parametrize("seed", SEEDS)
def test_pacman_corners_and_centre(seed: int) -> None:
    """The four corners and the centre are reachable corridors."""
    maze = _build(seed, perfect=False)
    reached = _reachable(maze)

    corners_and_centre: list[tuple[int, int]] = [
        (0, 0),
        (maze.width - 1, 0),
        (0, maze.height - 1),
        (maze.width - 1, maze.height - 1),
        ((maze.width - 1) // 2, (maze.height - 1) // 2),
    ]

    for cell in corners_and_centre:
        assert cell in reached


@pytest.mark.parametrize("seed", SEEDS)
def test_pacman_same_seed_same_maze(seed: int) -> None:
    """The same seed always builds the same Pac-Man maze."""
    first = _build(seed, perfect=False)
    second = _build(seed, perfect=False)
    other = _build(seed + 1, perfect=False)

    assert first.grid == second.grid
    assert first.grid != other.grid


@pytest.mark.parametrize("width, height", SMALL_BRAIDED_SIZES)
def test_pacman_small_mazes_have_loops(width: int, height: int) -> None:
    """Small Pac-Man mazes keep two loops and no 3x3 open area."""
    for seed in range(50):
        maze = _build(seed, width, height, perfect=False)
        reached = _reachable(maze)

        assert _count_passages(maze) >= (len(reached) - 1) + 2
        assert not _has_open_area(maze)


@pytest.mark.parametrize("width, height", TOO_SMALL_BRAIDED)
def test_small_pacman_raises(width: int, height: int) -> None:
    """A Pac-Man maze smaller than 3x3 raises MazeGeneratorError."""
    with pytest.raises(MazeGeneratorError):
        MazeGenerator(width=width,
                      height=height,
                      entry=(0, 0),
                      exit=(width - 1, height - 1),
                      perfect=False)
