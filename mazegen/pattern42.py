"""pattern42.py: cell mask that draws the "42" pattern in a maze."""


from typing import Final

PATTERN_42: Final = ("#.#.###",
                     "#.#...#",
                     "###.###",
                     "..#.#..",
                     "..#.###")


def pattern_42_cells(width: int, height: int) -> set[tuple[int, int]]:
    """    """
