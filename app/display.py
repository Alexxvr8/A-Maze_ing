"""display.py: render the maze in the window and run the menu."""


from typing import Final
from mazegen import EAST, NORTH, SOUTH, WEST
from mazegen import MazeGenerator, shortest_path
from mazegen.directions import ALL_DIRECTIONS, DELTAS, LETTERS
from mlx import Mlx


SCREEN_RATIO: Final = 0.8
MAX_CELL_SIZE: Final = 40
MIN_CELL_SIZE: Final = 1
HELP_HEIGHT: Final = 30
HELP_TEXT: Final = "R: new maze   P: path   C: colour   ESC: quit"

KEY_ESCAPE: Final = 65307
KEY_R: Final = 114
KEY_P: Final = 112
KEY_C: Final = 99
EVENT_CLOSE: Final = 33

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
    def __init__(self, generator: MazeGenerator) -> None:
        """Generate the maze and open the window.

        Args:
            generator: Maze generator. Its maze is generated here.

        Raises:
            RuntimeError: If MLX cannot open the connection, the window or
                the image.
        """
        generator.generate()
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
            self.width_px,
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
        self.byte_order = "little" if image_format == 0 else "big"

        self.show_path = False
        self.colour_index = 0
        self.path_cells: set[tuple[int, int]] = set()
        self._update_path()

    def _update_path(self) -> None:
        """Convert the shortest path from letters into the cells it crosses."""
        letters = shortest_path(
            self.generator.grid, self.generator.entry, self.generator.exit
        )
        moves = {LETTERS[d]: DELTAS[d] for d in ALL_DIRECTIONS}

        (x, y) = self.generator.entry
        cells = {(x, y)}
        for letter in letters:
            (dx, dy) = moves[letter]
            x += dx
            y += dy
            cells.add((x, y))
        self.path_cells = cells

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

    def draw(self) -> None:
        """Paint the maze in the image and show it in the window.

        Every wall is drawn once: the north and west wall of each cell, plus
        the south wall of the last row and the east wall of the last column.
        """
        inset = self.cell_size // 4
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
                elif self.show_path and cell in self.path_cells:
                    self._fill_rect(
                        px + inset,
                        py + inset,
                        self.cell_size - 2 * inset,
                        self.cell_size - 2 * inset,
                        PATH_COLOUR
                    )

                walls = self.generator.grid[y][x]
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

    def keyboard_input(self, key_code: int, param: object) -> None:
        """Handle a key and redraw if something changed.

        Args:
            key_code: X11 keysym of the key.
            param: Value given to the hook, not used.
        """
        if key_code == KEY_ESCAPE:
            self.destroy(param)
        elif key_code == KEY_R:
            self.generator.regenerate()
            self._update_path()
            self.draw()
        elif key_code == KEY_P:
            self.show_path = not self.show_path
            self.draw()
        elif key_code == KEY_C:
            self.colour_index = (self.colour_index + 1) % len(WALL_COLOURS)
            self.draw()

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

        self.draw()
        self.mlx.mlx_loop(self.mlx_ptr)

        self.mlx.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.mlx.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx.mlx_release(self.mlx_ptr)
