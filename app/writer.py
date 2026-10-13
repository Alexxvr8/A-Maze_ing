"""writer.py: write a maze to the hexadecimal output file format."""


def _convert_to_hex(n: int) -> str:
    """Convert a wall value into one lowercase hexadecimal character.

    Args:
        n: Wall value of a cell, from 0 to 15.

    Returns:
        The value as a single character, from "0" to "f".
    """
    match n:
        case 10:
            return "a"
        case 11:
            return "b"
        case 12:
            return "c"
        case 13:
            return "d"
        case 14:
            return "e"
        case 15:
            return "f"
        case _:
            return f"{n}"


def write_maze(
        path: str,
        grid: list[list[int]],
        entry: tuple[int, int],
        exit: tuple[int, int],
        solution: str) -> None:
    """Write a maze to a file using the hexadecimal output format.

    The file has one line per grid row with one hexadecimal character per
    cell, then an empty line, the entry as x,y, the exit as x,y and the
    solution path. Every line ends with a newline.

    Args:
        path: Path of the file to write. It is overwritten if it exists.
        grid: Maze as grid[y][x], with wall bits from 0 to 15.
        entry: Entry cell as (x, y).
        exit: Exit cell as (x, y).
        solution: Moves from entry to exit as letters, for example "SE".

    Raises:
        OSError: If the file cannot be written.
    """
    (x_entry, y_entry) = entry
    (x_exit, y_exit) = exit
    height = len(grid)
    width = len(grid[0])
    x = 0
    y = 0
    with open(path, "w", encoding="utf-8") as f:
        while y < height:
            x = 0
            while x < width:
                f.write(_convert_to_hex(grid[y][x]))
                x += 1
            f.write("\n")
            y += 1
        f.write(f"\n{x_entry},{y_entry}\n")
        f.write(f"{x_exit},{y_exit}\n")
        f.write(f"{solution}\n")
