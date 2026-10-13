"""mazegen: reusable package to generate and solve mazes.

Example:
    >>> from mazegen import MazeGenerator, shortest_path
    >>> maze = MazeGenerator(20, 15, (0, 0), (19, 14), seed=42)
    >>> maze.generate()
    >>> path = shortest_path(maze.grid, maze.entry, maze.exit)
"""


from mazegen.directions import EAST, NORTH, SOUTH, WEST
from mazegen.generator import MazeGenerator, MazeGeneratorError
from mazegen.solver import shortest_path


__all__ = [
    "MazeGenerator",
    "MazeGeneratorError",
    "shortest_path",
    "NORTH",
    "EAST",
    "SOUTH",
    "WEST",
]
