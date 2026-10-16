"""generator.py: MazeGenerator class for perfect and braided mazes."""


import random
from typing import Final

from mazegen.directions import (
    ALL_DIRECTIONS,
    ALL_WALLS,
    DELTAS,
    EAST,
    OPPOSITE,
    SOUTH,
)
from mazegen.pattern42 import pattern_42_cells


MIN_BRAIDED_SIZE: Final = 3
MIN_LOOPS: Final = 2


class MazeGeneratorError(ValueError):
    """Raised when the maze parameters are invalid."""


class MazeGenerator:
    """Generate perfect or braided mazes with an optional fixed seed."""

    def __init__(self, width: int, height: int,
                 entry: tuple[int, int], exit: tuple[int, int],
                 perfect: bool = True, seed: int | None = None) -> None:
        """Store and validate the maze parameters.

        Args:
            width: Number of columns.
            height: Number of rows.
            entry: Entry cell as (x, y).
            exit: Exit cell as (x, y).
            perfect: Whether the maze has a single path between cells.
            seed: Random seed, or None to pick one at random.

        Raises:
            MazeGeneratorError: If the size is not positive, or entry or
                exit are out of bounds, equal, or inside the "42" pattern,
                or a non-perfect maze is smaller than 3x3.
        """
        if width <= 0:
            raise MazeGeneratorError(f"width must be positive, got {width}")
        if height <= 0:
            raise MazeGeneratorError(
                f"height must be positive, got {height}"
            )
        self.width = width
        self.height = height

        self._check_coord(entry, "entry")
        self._check_coord(exit, "exit")
        if entry == exit:
            raise MazeGeneratorError(
                f"entry and exit must be different, both are {entry}"
            )

        self.pattern_cells: set[tuple[int, int]] = pattern_42_cells(
            width, height
        )
        self._check_outside_pattern(entry, "entry")
        self._check_outside_pattern(exit, "exit")
        self.entry = entry
        self.exit = exit

        self.perfect = perfect
        if not perfect and (width < MIN_BRAIDED_SIZE
                            or height < MIN_BRAIDED_SIZE):
            raise MazeGeneratorError(
                f"a non-perfect maze needs at least "
                f"{MIN_BRAIDED_SIZE}x{MIN_BRAIDED_SIZE} cells, "
                f"got {width}x{height}"
            )

        self.seed = random.randrange(2**32) if seed is None else seed
        self.grid: list[list[int]] = []

    def _inside(self, cell: tuple[int, int]) -> bool:
        """Return whether the cell is inside the maze."""
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

    def _check_coord(self, cell: tuple[int, int], name: str) -> None:
        """Raise MazeGeneratorError if the cell is outside the maze.

        Args:
            cell: Cell to check, as (x, y).
            name: Label used in the error message.

        Raises:
            MazeGeneratorError: If the cell is out of bounds.
        """
        if not self._inside(cell):
            raise MazeGeneratorError(
                f"{name} {cell} is outside the maze: "
                f"x must be 0-{self.width - 1}, y must be 0-{self.height - 1}"
            )

    def _check_outside_pattern(self, cell: tuple[int, int],
                               name: str) -> None:
        """Raise MazeGeneratorError if the cell belongs to the "42" pattern.

        Args:
            cell: Cell to check, as (x, y).
            name: Label used in the error message.

        Raises:
            MazeGeneratorError: If the cell is one of the pattern cells.
        """
        if cell in self.pattern_cells:
            raise MazeGeneratorError(
                f'{name} {cell} is inside the "42" pattern'
            )

    def _fill_grid(self) -> None:
        """Reset the grid so every cell has all four walls closed."""
        self.grid = [[ALL_WALLS] * self.width for _ in range(self.height)]

    def _open_wall(self, cell: tuple[int, int], direction: int) -> None:
        """Remove the wall between a cell and its neighbour.

        Both sides are updated so the walls stay coherent.

        Args:
            cell: Cell as (x, y).
            direction: Wall to open, one of the direction bits.

        Raises:
            MazeGeneratorError: If the neighbour is outside the maze.
        """
        x, y = cell
        dx, dy = DELTAS[direction]
        nx = x + dx
        ny = y + dy

        self._check_coord((nx, ny), "neighbour")

        self.grid[y][x] &= ~direction
        self.grid[ny][nx] &= ~OPPOSITE[direction]

    def _close_wall(self, cell: tuple[int, int], direction: int) -> None:
        """Close the wall between a cell and its neighbour.

        Both sides are updated so the walls stay coherent. It undoes
        _open_wall.

        Args:
            cell: Cell as (x, y).
            direction: Wall to close, one of the direction bits.

        Raises:
            MazeGeneratorError: If the neighbour is outside the maze.
        """
        x, y = cell
        dx, dy = DELTAS[direction]
        nx = x + dx
        ny = y + dy

        self._check_coord((nx, ny), "neighbour")

        self.grid[y][x] |= direction
        self.grid[ny][nx] |= OPPOSITE[direction]

    def _count_walls(self, cell: tuple[int, int]) -> int:
        """Return how many of the four walls of a cell are closed.

        Args:
            cell: Cell as (x, y).

        Returns:
            Number of closed walls, from 0 to 4.
        """
        x, y = cell
        walls = 0
        for direction in ALL_DIRECTIONS:
            if self.grid[y][x] & direction:
                walls += 1
        return walls

    def _is_dead_end(self, cell: tuple[int, int]) -> bool:
        """Return whether a cell is a dead end.

        A dead end has exactly three closed walls, so it has a single exit.
        Cells of the "42" pattern are never dead ends.

        Args:
            cell: Cell as (x, y).

        Returns:
            True if the cell is outside the "42" and has one exit.
        """
        return cell not in self.pattern_cells and self._count_walls(cell) == 3

    def _neighbours(
        self, cell: tuple[int, int]
    ) -> list[tuple[int, tuple[int, int]]]:
        """Return the neighbours a path can move to from a cell.

        A neighbour is valid if it is inside the maze and not part of the
        "42" pattern. The order is fixed by ALL_DIRECTIONS so results are
        reproducible.

        Args:
            cell: Cell as (x, y).

        Returns:
            List of (direction, neighbour) pairs.
        """
        x, y = cell
        moves: list[tuple[int, tuple[int, int]]] = []
        for direction in ALL_DIRECTIONS:
            dx, dy = DELTAS[direction]
            neighbour = (x + dx, y + dy)
            if self._inside(neighbour) and neighbour not in self.pattern_cells:
                moves.append((direction, neighbour))
        return moves

    def _unvisited_neighbours(
        self, cell: tuple[int, int], visited: set[tuple[int, int]]
    ) -> list[tuple[int, tuple[int, int]]]:
        """Return the neighbours of a cell that have not been visited yet.

        Args:
            cell: Cell as (x, y).
            visited: Cells already reached by the walk.

        Returns:
            List of (direction, neighbour) pairs still free to visit.
        """
        free: list[tuple[int, tuple[int, int]]] = []
        for direction, neighbour in self._neighbours(cell):
            if neighbour not in visited:
                free.append((direction, neighbour))
        return free

    def _backtracker(self, rng: random.Random) -> None:
        """Carve a perfect maze from the entry with a randomised DFS.

        The walk opens a wall to a random unvisited neighbour and backtracks
        when it gets stuck. A stack replaces recursion so large mazes do not
        hit Python's recursion limit.

        Args:
            rng: Random generator seeded with self.seed, shared with the
                rest of the generation so the maze stays reproducible.
        """
        visited: set[tuple[int, int]] = {self.entry}
        stack: list[tuple[int, int]] = [self.entry]

        while stack:
            current = stack[-1]
            options = self._unvisited_neighbours(current, visited)

            if not options:
                stack.pop()
                continue

            direction, next_cell = rng.choice(options)
            self._open_wall(current, direction)

            visited.add(next_cell)
            stack.append(next_cell)

    def _block_is_open(self, left: int, top: int) -> bool:
        """Return whether the 3x3 block at (left, top) has no inner walls.

        A block that does not fit inside the maze is never open.

        Args:
            left: Column of the top-left cell of the block.
            top: Row of the top-left cell of the block.

        Returns:
            True if all twelve inner walls of the block are open.
        """
        if (left < 0 or top < 0
                or left + 2 >= self.width or top + 2 >= self.height):
            return False

        for y in range(top, top + 3):
            for x in range(left, left + 3):
                if x < left + 2 and self.grid[y][x] & EAST:
                    return False
                if y < top + 2 and self.grid[y][x] & SOUTH:
                    return False

        return True

    def _touches_open_block(self, cell: tuple[int, int]) -> bool:
        """Return whether any 3x3 block containing the cell is fully open.

        Args:
            cell: Cell as (x, y).

        Returns:
            True if the cell belongs to at least one open 3x3 block.
        """
        x, y = cell
        for left in range(x - 2, x + 1):
            for top in range(y - 2, y + 1):
                if self._block_is_open(left, top):
                    return True
        return False

    def _remove_dead_end(
        self, cell: tuple[int, int], rng: random.Random
    ) -> None:
        """Open one wall of a dead end without creating a 3x3 open area.

        Neighbours that are dead ends too are tried first, so one opening
        can fix two dead ends. A wall that would create a 3x3 open area is
        closed again and the next option is tried.

        Args:
            cell: Dead-end cell as (x, y).
            rng: Random generator shared with the rest of the generation.
        """
        x, y = cell
        options: list[tuple[int, tuple[int, int]]] = []
        for direction, neighbour in self._neighbours(cell):
            if self.grid[y][x] & direction:
                options.append((direction, neighbour))

        rng.shuffle(options)
        options.sort(key=lambda option: not self._is_dead_end(option[1]))

        for direction, neighbour in options:
            self._open_wall(cell, direction)
            if (self._touches_open_block(cell)
                    or self._touches_open_block(neighbour)):
                self._close_wall(cell, direction)
                continue
            return

    def _braid(self, rng: random.Random) -> None:
        """Remove dead ends to add loops for the non-perfect mode.

        Cells are visited in a random order so loops are spread over the
        whole maze. A cell is only fixed if it is still a dead end when its
        turn comes, since fixing a neighbour may already have fixed it.

        Args:
            rng: Random generator shared with the rest of the generation.
        """
        cells: list[tuple[int, int]] = []
        for y in range(self.height):
            for x in range(self.width):
                cells.append((x, y))

        rng.shuffle(cells)

        for cell in cells:
            if self._is_dead_end(cell):
                self._remove_dead_end(cell, rng)

    def _count_passages(self) -> int:
        """Return how many open walls join two cells of the maze.

        Only the east and south walls of each cell are checked, so every
        passage is counted once.
        """
        grid = self.grid
        passages = 0

        for y in range(self.height):
            for x in range(self.width):
                if not (grid[y][x] & EAST):
                    passages += 1
                if not (grid[y][x] & SOUTH):
                    passages += 1
        return passages

    def _count_loops(self) -> int:
        """Return how many independent loops the maze has.

        A maze where every reachable cell is connected and there are no
        loops has one passage fewer than cells. Each extra passage adds
        one loop.

        Returns:
            Number of passages minus (reachable cells - 1).
        """
        reachable = self.width * self.height - len(self.pattern_cells)
        return self._count_passages() - (reachable - 1)

    def _ensure_loops(self, rng: random.Random) -> None:
        """Open extra walls until the maze has at least MIN_LOOPS loops.

        Candidate walls are tried in a random order. A wall that would
        create a 3x3 open area is closed again. Opening walls never adds
        dead ends, so the braided result is kept.

        Args:
            rng: Random generator shared with the rest of the generation.
        """
        candidates: list[tuple[tuple[int, int], int, tuple[int, int]]] = []

        for y in range(self.height):
            for x in range(self.width):
                for direction in (EAST, SOUTH):
                    dx, dy = DELTAS[direction]
                    cell = (x, y)
                    neighbour = (x + dx, y + dy)

                    if (self.grid[y][x] & direction
                            and self._inside(neighbour)
                            and cell not in self.pattern_cells
                            and neighbour not in self.pattern_cells):
                        candidates.append((cell, direction, neighbour))

        rng.shuffle(candidates)

        for cell, direction, neighbour in candidates:
            if self._count_loops() >= MIN_LOOPS:
                return
            self._open_wall(cell, direction)
            if (self._touches_open_block(cell)
                    or self._touches_open_block(neighbour)):
                self._close_wall(cell, direction)

    def generate(self) -> None:
        """Build the maze with the current seed.

        The grid is reset and a perfect maze is carved with the
        backtracker. If the maze is not perfect, dead ends are removed and
        extra walls are opened until it has at least MIN_LOOPS loops. Cells
        of the "42" pattern always keep their four walls. The same seed
        always produces the same maze.
        """
        rng = random.Random(self.seed)
        self._fill_grid()

        self._backtracker(rng)

        if not self.perfect:
            self._braid(rng)
            self._ensure_loops(rng)

    def regenerate(self) -> None:
        """Pick a new random seed and build a new maze with it."""
        self.seed = random.randrange(2**32)
        self.generate()
