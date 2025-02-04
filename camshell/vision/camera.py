from loguru import logger
from camshell.interfaces import Camera, Image, Size
from camshell.vision.gstream_pipeline import GStreamerPipeline
from camshell.vision import gstream_components as components


class MacosCamera(GStreamerPipeline, Camera):
    def __init__(self, **kwargs):
        super().__init__()
        self.pipeline_description = (
            components.AVFVideoSource(kwargs)
            # + components.VideoRaw(kwargs)
            + components.VideoRate(kwargs)
            + components.VideoConvert(kwargs)
            + components.Queue()
            + components.AppSink()
        )
        self.__optimized_size: Size | None = None

    def optimize_for(self, size: Size) -> None:
        self.__optimized_size = size

    def read(self) -> Image:
        with self.lock:
            buffer = self.buffer
            caps = self.caps
            if buffer is None or caps is None:
                raise RuntimeError("Buffer or caps is None")

            original_size = Size(
                width=caps.get_structure(0).get_value("width"),
                height=caps.get_structure(0).get_value("height"),
            )
            buffer_size = buffer.get_size()
            data = buffer.extract_dup(0, buffer_size)
            image = Image(data, original_size)

            if self.__optimized_size is None:
                self.__optimized_size = original_size
            return image.resize(self.__optimized_size)
