"""pattern42.py: cell mask that draws the "42" pattern in a maze."""


from typing import Final


PATTERN_42: Final = (
    "#.#.###",
    "#.#...#",
    "###.###",
    "..#.#..",
    "..#.###",
)
PATTERN_WIDTH: Final = len(PATTERN_42[0])
PATTERN_HEIGHT: Final = len(PATTERN_42)
MIN_WIDTH: Final = PATTERN_WIDTH + 2
MIN_HEIGHT: Final = PATTERN_HEIGHT + 2


def pattern_42_cells(width: int, height: int) -> set[tuple[int, int]]:
    """Return the cells that draw the "42" centred in the maze.

    Args:
        width: Number of columns of the maze.
        height: Number of rows of the maze.

    Returns:
        Set of (x, y) cells of the pattern, or an empty set if the maze is
        too small to fit it with a one-cell margin.
    """
    if width < MIN_WIDTH or height < MIN_HEIGHT:
        return set()

    offset_x = (width - PATTERN_WIDTH) // 2
    offset_y = (height - PATTERN_HEIGHT) // 2

    cells: set[tuple[int, int]] = set()
    for row_index, row in enumerate(PATTERN_42):
        for col_index, char in enumerate(row):
            if char == "#":
                cells.add((col_index + offset_x, row_index + offset_y))
    return cells
