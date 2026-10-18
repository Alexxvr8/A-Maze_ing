"""display.py: render the maze in the window and run the menu."""


import time
from typing import Final, Literal
from mazegen import EAST, NORTH, SOUTH, WEST
from mazegen import MazeGenerator, shortest_path
from mazegen.directions import (
    ALL_DIRECTIONS,
    DELTAS,
    LETTERS,
    OPPOSITE,
    ALL_WALLS
)
from mlx import Mlx


SCREEN_RATIO: Final = 0.8
MAX_CELL_SIZE: Final = 40
MIN_CELL_SIZE: Final = 1
HELP_HEIGHT: Final = 30
MIN_WINDOW_WIDTH: Final = 440
HELP_TEXT: Final = (
    "R: new maze   P: path   C: colour   A: animate   ESC: quit"
)

KEY_ESCAPE: Final = 65307
KEY_A: Final = 97
KEY_R: Final = 114
KEY_P: Final = 112
KEY_C: Final = 99
EVENT_CLOSE: Final = 33

FRAME_DELAY: Final = 0.03
ANIMATION_SECONDS: Final = 4.0
ANIMATION_FRAMES: Final = int(ANIMATION_SECONDS / FRAME_DELAY)
GENERATE: Final = "generate"
PATH: Final = "path"

BG_COLOUR: Final = 0xFF000000
TEXT_COLOUR: Final = 0xFFFFFFFF
ENTRY_COLOUR: Final = 0xFF2ECC40
EXIT_COLOUR: Final = 0xFFFF4136
PATH_COLOUR: Final = 0xFFFFDC00
PATTERN_COLOUR: Final = 0xFF808080
WALL_COLOURS: Final = (
    0xFFFFFFFF,
    0xFF00BFFF,
    0xFFFF8800,
    0xFFFF00FF,
    0xFF00FF7F,
)


class Display:
    """MiniLibX window that shows a maze and reacts to the keyboard.

    Keys: R new maze, P show or hide the path (animated), C wall colour,
    A replay the generation, ESC or the window cross to quit.
    """
    def __init__(self, generator: MazeGenerator) -> None:
        """Open the window for a maze that is already generated.

        Args:
            generator: Maze generator, with generate() already called.

        Raises:
            RuntimeError: If MLX cannot open the connection, the window or
                the image.
        """
        self.generator = generator

        self.mlx = Mlx()
        self.mlx_ptr = self.mlx.mlx_init()
        if self.mlx_ptr is None:
            raise RuntimeError("MLX could not connect to the display.")

        (_, screen_w, screen_h) = self.mlx.mlx_get_screen_size(self.mlx_ptr)
        if screen_w == 0 or screen_h == 0:
            self.cell_size = MAX_CELL_SIZE
        else:
            fit_w = int(screen_w * SCREEN_RATIO) // generator.width
            fit_h = int(screen_h * SCREEN_RATIO) // generator.height
            fit = min(fit_w, fit_h, MAX_CELL_SIZE)
            self.cell_size = max(MIN_CELL_SIZE, fit)

        self.wall_thickness = max(1, self.cell_size // 10)
        self.width_px = generator.width * self.cell_size
        self.height_px = generator.height * self.cell_size

        self.win_ptr = self.mlx.mlx_new_window(
            self.mlx_ptr,
            max(self.width_px, MIN_WINDOW_WIDTH),
            self.height_px + HELP_HEIGHT,
            "A-Maze-ing"
        )
        self.img_ptr = self.mlx.mlx_new_image(
            self.mlx_ptr,
            self.width_px,
            self.height_px
        )
        if self.win_ptr is None or self.img_ptr is None:
            raise RuntimeError("MLX could not create the window or image.")

        (self.buffer, bits, self.size_line, image_format) = (
            self.mlx.mlx_get_data_addr(self.img_ptr)
        )
        self.pixel_bytes = bits // 8
        self.byte_order: Literal["little", "big"] = (
            "little" if image_format == 0 else "big"
        )

        self.show_path = False
        self.path_after = False
        self.colour_index = 0
        self.view_grid: list[list[int]] = generator.grid

        self.animation: str | None = None
        self.last_frame = 0.0
        self.step_index = 0
        self.steps_per_frame = 1
        self.path_per_frame = 1
        self.path_progress = 0
        self.path_list: list[tuple[int, int]] = []
        self.path_order: dict[tuple[int, int], int] = {}
        self._update_path()

    def _update_path(self) -> None:
        """Convert the shortest path from letters into the cells it crosses."""
        letters = shortest_path(
            self.generator.grid, self.generator.entry, self.generator.exit
        )
        moves = {LETTERS[d]: DELTAS[d] for d in ALL_DIRECTIONS}

        (x, y) = self.generator.entry
        cells = [(x, y)]
        for letter in letters:
            (dx, dy) = moves[letter]
            x += dx
            y += dy
            cells.append((x, y))

        self.path_list = cells
        self.path_order = {cell: i for i, cell in enumerate(cells)}
        self.path_progress = len(cells)

    def _path_visible(self, cell: tuple[int, int]) -> bool:
        """Return whether the cell is already part of the shown path."""
        order = self.path_order.get(cell)
        return order is not None and order < self.path_progress

    def _fill_rect(
            self,
            x: int,
            y: int,
            width: int,
            height: int,
            colour: int
    ) -> None:
        """Paint a filled rectangle of one colour in the image buffer.

        Args:
            x: Left pixel of the rectangle.
            y: Top pixel of the rectangle.
            width: Width in pixels.
            height: Height in pixels.
            colour: Colour as 0xAARRGGBB.
        """
        pixel = colour.to_bytes(self.pixel_bytes, self.byte_order)
        row = pixel * width
        for line in range(y, y + height):
            start = line * self.size_line + x * self.pixel_bytes
            self.buffer[start:start + len(row)] = row

    def _cell_colour(self, cell: tuple[int, int]) -> int | None:
        """Return the fill colour of a cell, or None if it has none.

        Args:
            cell: Cell as (x, y).

        Returns:
            Colour for the entry, the exit or the "42" pattern, or None.
        """
        if cell == self.generator.entry:
            return ENTRY_COLOUR
        if cell == self.generator.exit:
            return EXIT_COLOUR
        if cell in self.generator.pattern_cells:
            return PATTERN_COLOUR
        return None

    def _paint_path_cell(self, cell: tuple[int, int]) -> None:
        """Paint one path cell, without redrawing the whole maze.

        Args:
            cell: Cell as (x, y). Entry, exit and "42" cells are skipped.
        """
        if self._cell_colour(cell) is not None:
            return

        inset = self.cell_size // 4
        self._fill_rect(
            cell[0] * self.cell_size + inset,
            cell[1] * self.cell_size + inset,
            self.cell_size - 2 * inset,
            self.cell_size - 2 * inset,
            PATH_COLOUR
        )

    def _present(self) -> None:
        """Show the image and the help text in the window."""
        self.mlx.mlx_put_image_to_window(
            self.mlx_ptr,
            self.win_ptr,
            self.img_ptr,
            0,
            0
        )
        self.mlx.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            10,
            self.height_px + 20,
            TEXT_COLOUR,
            HELP_TEXT
        )

    def draw(self) -> None:
        """Paint the maze in the image and show it in the window.

        Every wall is drawn once: the north and west wall of each cell, plus
        the south wall of the last row and the east wall of the last column.
        """
        wall_colour = WALL_COLOURS[self.colour_index]

        self._fill_rect(
            0,
            0,
            self.width_px,
            self.height_px,
            BG_COLOUR
        )

        for y in range(self.generator.height):
            for x in range(self.generator.width):
                px = x * self.cell_size
                py = y * self.cell_size
                cell = (x, y)

                fill = self._cell_colour(cell)
                if fill is not None:
                    self._fill_rect(
                        px,
                        py,
                        self.cell_size,
                        self.cell_size,
                        fill
                    )
                elif self.show_path and self._path_visible(cell):
                    self._paint_path_cell(cell)

                walls = self.view_grid[y][x]
                if walls & NORTH:
                    self._fill_rect(
                        px,
                        py,
                        self.cell_size,
                        self.wall_thickness,
                        wall_colour
                    )
                if walls & WEST:
                    self._fill_rect(
                        px,
                        py,
                        self.wall_thickness,
                        self.cell_size,
                        wall_colour
                    )
                if walls & SOUTH and y == self.generator.height - 1:
                    self._fill_rect(
                        px,
                        py + self.cell_size - self.wall_thickness,
                        self.cell_size,
                        self.wall_thickness,
                        wall_colour
                    )
                if walls & EAST and x == self.generator.width - 1:
                    self._fill_rect(
                        px + self.cell_size - self.wall_thickness,
                        py,
                        self.wall_thickness,
                        self.cell_size,
                        wall_colour
                    )
        self._present()

    def _start_generation(self) -> None:
        """Replay the generator steps on a closed grid."""
        gen = self.generator
        self.steps_per_frame = max(1, len(gen.steps) // ANIMATION_FRAMES)
        self.view_grid = [[ALL_WALLS] * gen.width for _ in range(gen.height)]
        self.step_index = 0
        self.show_path = False
        self.animation = GENERATE
        self.draw()

    def _advance_generation(self) -> None:
        """Open the next group of walls and redraw."""
        steps = self.generator.steps
        stop = min(len(steps), self.step_index + self.steps_per_frame)

        for (x, y), direction in steps[self.step_index:stop]:
            dx, dy = DELTAS[direction]
            self.view_grid[y][x] &= ~direction
            self.view_grid[y + dy][x + dx] &= ~OPPOSITE[direction]

        self.step_index = stop
        self.draw()
        if stop >= len(steps):
            self.view_grid = self.generator.grid
            self.animation = None
            if self.path_after:
                self.path_after = False
                self._start_path()

    def _start_path(self) -> None:
        """Start showing the path from the entry towards the exit."""
        self.path_per_frame = max(1, len(self.path_list) // ANIMATION_FRAMES)
        self.path_progress = 0
        self.show_path = True
        self.animation = PATH
        self.draw()

    def _advance_path(self) -> None:
        """Paint the next cells of the path, from the entry to the exit."""
        start = self.path_progress
        stop = min(len(self.path_list), start + self.path_per_frame)

        for cell in self.path_list[start:stop]:
            self._paint_path_cell(cell)

        self.path_progress = stop
        self._present()
        if stop >= len(self.path_list):
            self.animation = None

    def update(self, param: object) -> None:
        """Loop hook: advance the running animation at a fixed frame rate.

        Args:
            param: Value given to the hook, not used.
        """
        if self.animation is None:
            return

        now = time.monotonic()
        if now - self.last_frame < FRAME_DELAY:
            return

        self.last_frame = now
        if self.animation == GENERATE:
            self._advance_generation()
        else:
            self._advance_path()

    def keyboard_input(self, key_code: int, param: object) -> None:
        """Handle a key and redraw if something changed.

        Args:
            key_code: X11 keysym of the key.
            param: Value given to the hook, not used.
        """
        if key_code == KEY_ESCAPE:
            self.destroy(param)
        elif key_code == KEY_R:
            self.animation = None
            self.path_after = self.show_path or self.path_after
            self.generator.regenerate()
            self.view_grid = self.generator.grid
            self._update_path()
            self._start_generation()
        elif key_code == KEY_P:
            if self.animation == GENERATE:
                return
            if self.show_path:
                self.show_path = False
                self.animation = None
                self.draw()
            else:
                self._start_path()
        elif key_code == KEY_C:
            self.colour_index = (self.colour_index + 1) % len(WALL_COLOURS)
            self.draw()
        elif key_code == KEY_A:
            self.path_after = self.show_path or self.path_after
            self._start_generation()

    def destroy(self, param: object) -> None:
        """Ask MLX to leave the event loop.

        The resources are freed in run() once the loop has ended.

        Args:
            param: Value given to the hook, not used.
        """
        self.mlx.mlx_loop_exit(self.mlx_ptr)

    def run(self) -> None:
        """Draw the maze, wait for events and free MLX when the loop ends."""
        self.mlx.mlx_key_hook(self.win_ptr, self.keyboard_input, None)
        self.mlx.mlx_hook(self.win_ptr, EVENT_CLOSE, 0, self.destroy, None)
        self.mlx.mlx_loop_hook(self.mlx_ptr, self.update, None)

        self.draw()
        self.mlx.mlx_loop(self.mlx_ptr)

        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_release(self.mlx_ptr)
