"""directions.py: wall bits, moves and letters for the four directions."""


from typing import Final


NORTH: Final = 1
EAST: Final = 2
SOUTH: Final = 4
WEST: Final = 8

ALL_DIRECTIONS: Final = (NORTH, EAST, SOUTH, WEST)

DELTAS: Final[dict[int, tuple[int, int]]] = {
    NORTH: (0, -1),
    EAST: (1, 0),
    SOUTH: (0, 1),
    WEST: (-1, 0)
}

OPPOSITE: Final[dict[int, int]] = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST
}

LETTERS: Final[dict[int, str]] = {
    NORTH: 'N',
    EAST: 'E',
    SOUTH: 'S',
    WEST: 'W'
}
