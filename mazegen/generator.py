"""generator.py: MazeGenerator class for perfect and braided mazes."""


from mazegen.directions import ALL_WALLS, DELTAS, OPPOSITE


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
                exit are out of bounds or equal.
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
        self.entry = entry
        self.exit = exit

        self.perfect = perfect
        self.seed = seed
        self.grid: list[list[int]] = []
        self.pattern_cells: set[tuple[int, int]] = set()

    def _check_coord(self, coords: tuple[int, int], name: str) -> None:
        """Raise MazeGeneratorError if the cell is outside the maze.

        Args:
            coords: Cell to check, as (x, y).
            name: Label used in the error message.

        Raises:
            MazeGeneratorError: If the cell is out of bounds.
        """
        x, y = coords
        if not 0 <= x < self.width or not 0 <= y < self.height:
            raise MazeGeneratorError(
                f"{name} {coords} is outside the maze: "
                f"x must be 0-{self.width - 1}, y must be 0-{self.height - 1}"
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
