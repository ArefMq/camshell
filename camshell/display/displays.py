from dataclasses import dataclass, field
import time
from typing import Generator
from rich.console import Console
from rich.text import Text
from camshell.interfaces import Display as DisplayInterface, Image, Size


@dataclass
class PixelPair:
    x: int
    y: int
    top_r: int
    top_g: int
    top_b: int
    bottom_r: int
    bottom_g: int
    bottom_b: int

    def distance_to(self, other: "PixelPair") -> float:
        return max(
            # Top pixel
            ((self.top_r - other.top_r) << 1)
            + ((self.top_g - other.top_g) << 1)
            + ((self.top_b - other.top_b) << 1),
            # Bottom pixel
            ((self.bottom_r - other.bottom_r) << 1)
            + ((self.bottom_g - other.bottom_g) << 1)
            + ((self.bottom_b - other.bottom_b) << 1),
        )

    def __sub__(self, other: "PixelPair") -> "Change":
        return Change.from_pixels(self, other)

    def __eq__(self, value) -> bool:
        return (
            self.x == value.x
            and self.y == value.y
            and self.top_r == value.top_r
            and self.top_g == value.top_g
            and self.top_b == value.top_b
            and self.bottom_r == value.bottom_r
            and self.bottom_g == value.bottom_g
            and self.bottom_b == value.bottom_b
        )

    @staticmethod
    def __adjust_brightness(r: int, g: int, b: int) -> tuple[int, int, int]:
        FACTOR = 1.18
        return (
            min(int(r * FACTOR), 255),
            min(int(g * FACTOR), 255),
            min(int(b * FACTOR), 255),
        )

    def resolve_pixel(self) -> str:
        b1, g1, r1 = self.bottom_b, self.bottom_g, self.bottom_r
        b2, g2, r2 = self.__adjust_brightness(self.top_b, self.top_g, self.top_r)
        color = f"[rgb({r1},{g1},{b1}) on rgb({r2},{g2},{b2})]▄"
        return Text(f"\033[{self.y + 1};{self.x + 1}H") + Text.from_markup(color)

    @classmethod
    def from_image(cls, image: Image, x: int, y: int) -> "PixelPair":
        tb, tg, tr = image.get_rgb(x, y * 2)
        bb, bg, br = image.get_rgb(x, y * 2 + 1)
        return cls(x, y, tr, tg, tb, br, bg, bb)


@dataclass
class Change:
    new_pixel: PixelPair
    diff: float

    @classmethod
    def from_pixels(cls, old_pixel: PixelPair, new_pixel: PixelPair) -> "Change":
        return cls(new_pixel, new_pixel.distance_to(old_pixel))

    @classmethod
    def NewPixel(cls, pixel: PixelPair) -> "Change":
        return cls(pixel, float("inf"))


@dataclass
class StreamBuffer:
    __buffer: dict[tuple[int, int], PixelPair] = field(default_factory=dict)
    __changes: list[Change] = field(default_factory=list)

    def ignore_the_rest(self) -> None:
        self.__changes = []

    def set(self, x: int, y: int, p: PixelPair) -> None:
        if (x, y) not in self.__buffer:
            self.__changes.append(Change.NewPixel(p))
        elif self.__buffer[(x, y)] == p:
            return
        else:
            self.__changes.append(self.__buffer[(x, y)] - p)
        self.__buffer[(x, y)] = p

    def changes(self) -> Generator[Change, None, None]:
        for change in sorted(self.__changes, key=lambda x: x.diff):
            yield change

    def pixels(self) -> Generator[PixelPair, None, None]:
        for change in self.changes():
            yield change.new_pixel


class CursesScreen(DisplayInterface):
    """Curses-based screen renderer for 256-color terminals."""

    WARM_UP_FRAMES = 3

    def __init__(
        self,
        max_size: Size | None = None,
        frame_time_limit: int | None = None,
    ) -> None:
        self.__buffer = StreamBuffer()
        self.__screen_size: Size | None = None
        self.max_size = max_size
        self.console = Console()
        self.frame_time_limit = frame_time_limit
        self.frames = 0

    def initialize(self) -> None:
        self.console.clear()
        self.frames = 0
        print("\033[?25l", end="", flush=True)  # Hide cursor

    def finalize(self) -> None:
        self.console.clear()
        print("\033[?25h", end="", flush=True)  # Show cursor back

    def refresh(self) -> None:
        t = time.monotonic()
        for p in self.__buffer.pixels():
            self.console.print(
                p.resolve_pixel(),
                end="",
                no_wrap=True,
                soft_wrap=False,
            )

            if self.frames > self.WARM_UP_FRAMES and self.frame_time_limit:
                if time.monotonic() - t > self.frame_time_limit:
                    break

        self.__buffer.ignore_the_rest()
        self.frames += 1

    def screen_get_size(self) -> Size:
        if self.__screen_size is None:
            width, height = self.console.size
            self.__screen_size = Size(width - 5, height - 5)
        if self.max_size is None:
            return self.__screen_size

        return Size(
            min(self.__screen_size.width, self.max_size.width),
            min(self.__screen_size.height, self.max_size.height),
        )

    def get_size(self) -> Size:
        size = self.screen_get_size()
        return Size(size.width, size.height * 2)

    def render(self, image: Image) -> None:
        size = self.screen_get_size()
        for y in range(min(image.size.height // 2, size.height)):
            for x in range(min(image.size.width, size.width)):
                self.__buffer.set(x, y, PixelPair.from_image(image, x, y))

        self.refresh()
