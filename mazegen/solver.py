"""solver.py: shortest path search between two maze cells."""


from collections import deque

from mazegen.directions import ALL_DIRECTIONS, DELTAS, LETTERS


def shortest_path(
        grid: list[list[int]],
        entry: tuple[int, int],
        exit: tuple[int, int]) -> str:
    """Find the shortest path between two cells of a maze.

    Args:
        grid: Maze as grid[y][x], with a wall bit set to 1 when closed.
        entry: Start cell as (x, y).
        exit: Goal cell as (x, y).

    Returns:
        The moves from entry to exit as letters, for example "ESSEN".

    Raises:
        ValueError: If there is no path from entry to exit.
    """
    height = len(grid)
    width = len(grid[0])

    queue = deque([entry])
    previous: dict[
        tuple[int, int], tuple[tuple[int, int], str] | None
    ] = {entry: None}

    while queue:
        x, y = queue.popleft()
        if (x, y) == exit:
            break
        for direction in ALL_DIRECTIONS:
            if grid[y][x] & direction:
                continue

            (dx, dy) = DELTAS[direction]
            nx = dx + x
            ny = dy + y

            if nx < 0 or nx >= width or ny < 0 or ny >= height:
                continue
            if (nx, ny) in previous:
                continue
            previous[(nx, ny)] = ((x, y), LETTERS[direction])
            queue.append((nx, ny))

    if exit not in previous:
        raise ValueError(f"No path from {entry} to {exit}.")

    letters: list[str] = []
    step = previous[exit]
    while step is not None:
        (previous_coord, letter) = step
        letters.append(letter)
        step = previous[previous_coord]

    return "".join(reversed(letters))
