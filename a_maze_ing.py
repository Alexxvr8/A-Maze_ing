#!/usr/bin/env python3
"""a_maze_ing.py: entry point that reads a config file and builds a maze."""


import sys
from app.config_parser import parse_config, ConfigError
from app.writer import write_maze
from app.display import Display
from mazegen import MazeGenerator, MazeGeneratorError
from mazegen.solver import shortest_path


def main() -> int:
    """Run the maze generator from the command line.

    Reads the configuration file given as the only argument, generates the
    maze, writes it to the output file and opens the window. Errors are
    printed to stderr without a traceback.

    Returns:
        0 if the program ends normally, 1 if the arguments are wrong or any
        error happens while reading the config, generating the maze, writing
        the file or opening the window.
    """
    if len(sys.argv) != 2:
        print("Usage: python3 a_maze_ing.py <config_file>", file=sys.stderr)
        return 1
    try:
        maze_config = parse_config(sys.argv[1])
        generator = MazeGenerator(
            maze_config.width,
            maze_config.height,
            maze_config.entry,
            maze_config.exit_,
            maze_config.perfect,
            maze_config.seed,
            maze_config.algorithm
        )
        generator.generate()

        if len(generator.pattern_cells) == 0:
            print(
                "Warning: maze too small, generated without the 42 pattern",
                file=sys.stderr
            )

        if maze_config.seed is None:
            print(f"Seed: {generator.seed}")

        write_maze(
            maze_config.output_file,
            generator.grid,
            generator.entry,
            generator.exit,
            shortest_path(
                generator.grid,
                generator.entry,
                generator.exit
            )
        )

        Display(generator).run()
        print("=== End of Program ===")
    except (
        ConfigError,
        MazeGeneratorError,
        ValueError,
        OSError,
        RuntimeError
    ) as e:
        print(e, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
