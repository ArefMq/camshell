import curses

from camshell.interfaces import Display, Image, Size


class CursesScreen(Display):
    """Curses-based screen renderer for 256-color terminals."""

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~ Overload these to create custom color maps ~~~~~~~~~~~~~~~~~~
    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    CHARMAP = " .:-=+*#%@"

    def init_colors(self) -> None:
        curses.start_color()
        if not curses.has_colors():
            raise RuntimeError("Terminal does not support colors")
        self.max_colors = curses.COLORS
        curses.use_default_colors()
        for i in range(1, min(curses.COLORS, 256)):
            curses.init_pair(i, i, self.background_color)

    def get_color_index(self, r: int, g: int, b: int) -> int:
        return 16 + (36 * (r // 51)) + (6 * (g // 51)) + (b // 51)

    def get_character(self, r: int, g: int, b: int, intensity: int) -> str:
        index = intensity // (256 // (len(self.CHARMAP) - 1))
        char = self.CHARMAP[index]
        return char

    # ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def __init__(self, mono_color: bool = False) -> None:
        self.mono_color = mono_color
        self.screen = None
        self.max_colors = 0
        self.background_color = -1

    def initialize(self) -> None:
        self.screen = curses.initscr()
        curses.noecho()
        curses.cbreak()
        self.screen.keypad(True)
        curses.curs_set(0)
        if not self.mono_color:
            self.init_colors()

    def finalize(self) -> None:
        if self.screen is None:
            return
        curses.curs_set(1)
        self.screen.keypad(False)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        self.screen = None

    def get_size(self) -> Size:
        assert self.screen is not None, "Screen is not initialized"
        return Size(
            width=self.screen.getmaxyx()[1] - 1, height=self.screen.getmaxyx()[0] - 1
        )

    def resolve_pixel(self, image: Image, x: int, y: int) -> tuple[str, int]:
        b, g, r = image.get_rgb(x, y)
        intensity = int(image.get_intensity(x, y))
        char = self.get_character(r, g, b, intensity)
        if self.mono_color:
            return char, 127
        return char, self.get_color_index(r, g, b)

    def render(self, image: Image) -> None:
        assert self.screen is not None, "Screen is not initialized"

        screen_size = self.get_size()
        for y in range(min(image.size.height, screen_size.height)):
            for x in range(min(image.size.width, screen_size.width)):
                char, color = self.resolve_pixel(image, x, y)
                self.screen.addch(y, x, char, curses.color_pair(color))

        self.screen.refresh()


class CursesScreenImproved(CursesScreen):
    CHARMAP = " .:-=+*#%@"

    def __init__(
        self,
        mono_color=False,
        gamma: tuple[float, float, float, float] = (1.1, 1.0, 1.0, 10.0),
    ):
        super().__init__(mono_color)
        self.color_gamma = gamma[:3]
        self.intensity_gamma = gamma[3]

    def get_color_index(self, r: int, g: int, b: int) -> int:
        r = int((r / 255.0) ** (1.0 / self.color_gamma[0]) * 255.0)
        g = int((g / 255.0) ** (1.0 / self.color_gamma[1]) * 255.0)
        b = int((b / 255.0) ** (1.0 / self.color_gamma[2]) * 255.0)
        return super().get_color_index(r, g, b)

    def get_character(self, r: int, g: int, b: int, intensity: int) -> str:
        normalized_intensity = intensity / 255.0
        corrected_intensity = normalized_intensity ** (1.0 / self.intensity_gamma)

        index = int(corrected_intensity * (len(self.CHARMAP) - 1))
        char = self.CHARMAP[index]
        return char
