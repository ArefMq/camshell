from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class Size:
    width: int
    height: int

    def __truediv__(self, other: "Size") -> "Size":
        return self.width / other.width, self.height / other.height

    def __getitem__(self, index: int) -> int:
        assert index in (0, 1), "Index must be 0 or 1"
        return self.width if index == 0 else self.height

@dataclass
class Image:
    data: bytes # 3 Dimensional array of bytes (Width * Height * 3)
    size: Size
    _coloured: bool = True

    def mono(self) -> "Image":
        return Image(self.data, self.size, _coloured=False)

    def get_row(self, y: int) -> bytes:
        if self._coloured:
            return self.data[y * self.size.width * 3 : (y + 1) * self.size.width * 3]
        return self.data[y * self.size.width : (y + 1) * self.size.width]
    
    def __getslice__(self, x: int, y: int) -> bytes:
        if self._coloured:
            return self.get_row(y)[x * 3 : (x + 1) * 3]
        return self.get_row(y)[x]
    
    def __iter__(self):
        for y in range(self.size.height):
            yield self.get_row(y)
    
    def get_rgb(self, x: int, y: int) -> tuple[int, int, int]:
        assert self._coloured, "Image is not coloured"
        data = self.__getslice__(x, y)
        return data[0], data[1], data[2]
    
    def get_intensity(self, x: int, y: int) -> int:
        if self._coloured:
            r, g, b = self.get_rgb(x, y)
            return 0.299 * r + 0.587 * g + 0.114 * b
        return self.__getslice__(x, y)
    
    # def resize(self, newSize: Size) -> "Image":
    #     if newSize == self.size:
    #         return self
    #     if not self._coloured:
    #         raise NotImplementedError
        
    #     scale = self.size / newSize
    #     data = bytearray([0] * (newSize.width * newSize.height * 3))

    #     for y in range(newSize.height):
    #         for x in range(newSize.width):
    #             old_x, old_y = int(x * scale[0]), int(y * scale[1])
    #             data[(y * newSize.width + x) * 3 : (y * newSize.width + x + 1) * 3] = self.__getslice__(old_x, old_y)
    #     return Image(data, newSize)

    def resize(self, newSize: Size) -> "Image":
        if newSize == self.size:
            return self
        if not self._coloured:
            raise NotImplementedError

        scale = self.size / newSize
        data = bytearray([0] * (newSize.width * newSize.height * 3))

        for y in range(newSize.height):
            for x in range(newSize.width):
                # Calculate the position in the original image
                old_x = (x + 0.5) * scale[0] - 0.5
                old_y = (y + 0.5) * scale[1] - 0.5

                # Get surrounding pixel coordinates
                x0, y0 = int(old_x), int(old_y)
                x1, y1 = min(x0 + 1, self.size.width - 1), min(y0 + 1, self.size.height - 1)

                # Bilinear interpolation to calculate the weighted average of the neighboring pixels
                dx, dy = old_x - x0, old_y - y0
                top_left = self.__getslice__(x0, y0)
                top_right = self.__getslice__(x1, y0)
                bottom_left = self.__getslice__(x0, y1)
                bottom_right = self.__getslice__(x1, y1)

                top = [(1 - dx) * top_left[i] + dx * top_right[i] for i in range(3)]
                bottom = [(1 - dx) * bottom_left[i] + dx * bottom_right[i] for i in range(3)]
                pixel = [(1 - dy) * top[i] + dy * bottom[i] for i in range(3)]

                # Store the new pixel value
                data[(y * newSize.width + x) * 3 : (y * newSize.width + x + 1) * 3] = bytearray([int(v) for v in pixel])

        return Image(data, newSize)


class Camera(ABC):
    def initialize(self) -> None: ...

    def finalize(self) -> None: ...

    def optimize_for(self, size: Size) -> None: ...

    @abstractmethod
    def read(self) -> Image: ...


class Display(ABC):
    def initialize(self) -> None: ...

    def finalize(self) -> None: ...

    @abstractmethod
    def get_size(self) -> Size: ...

    @abstractmethod
    def render(self, image: Image) -> None: ...
