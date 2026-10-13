"""generator.py: MazeGenerator class for perfect and braided mazes."""


import random

from mazegen.directions import ALL_DIRECTIONS, ALL_WALLS, DELTAS, OPPOSITE
from mazegen.pattern42 import pattern_42_cells


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
                exit are out of bounds, equal, or inside the "42" pattern.
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
        self.seed = random.randrange(2**32) if seed is None else seed
        self.grid: list[list[int]] = []

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

    def _inside(self, cell: tuple[int, int]) -> bool:
        """Return whether the cell is inside the maze."""
        x, y = cell
        return 0 <= x < self.width and 0 <= y < self.height

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

    def generate(self) -> None:
        """Build a perfect maze with a randomised depth-first search.

        Starting from the entry, the walk opens a wall to a random
        unvisited neighbour, and backtracks when it reaches a dead end. A
        stack replaces recursion so large mazes do not hit Python's
        recursion limit. Cells of the "42" pattern are never visited, so
        they keep all four walls.

        The same seed always produces the same maze.
        """
        rng = random.Random(self.seed)
        self._fill_grid()

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

    def regenerate(self) -> None:
        """Pick a new random seed and build a new maze with it."""
        self.seed = random.randrange(2**32)
        self.generate()
