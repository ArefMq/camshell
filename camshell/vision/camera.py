from enum import Enum
from loguru import logger
from camshell.interfaces import Camera, Image, Size
from camshell.vision import gstream_components as components
from camshell.vision.gstream_pipeline import GStreamerPipeline


class GenericCamera(GStreamerPipeline, Camera):
    """Generic camera that reads from a GStream device."""

    class Source(Enum):
        V4L2 = "v4l2"
        AVF = "avf"
        FILE = "file"

        def to_gstream(self, kwargs) -> components.GStreamComponent:
            t = {
                self.V4L2: components.V4L2Source,
                self.AVF: components.AVFVideoSource,
                self.FILE: components.FileSource,
            }[self]
            return t(kwargs)

    def __init__(self, **kwargs):
        super().__init__()
        source = GenericCamera.Source(kwargs.pop("source", "v4l2"))
        self.pipeline_description = (
            source.to_gstream(kwargs)
            + components.VideoRate(kwargs)
            + components.VideoConvert(kwargs)
            + components.Queue()
            + components.AppSink()
        )
        logger.debug(f"Pipeline: {self.pipeline_description}")
        self.__optimized_size: Size | None = None

    def initialize(self, timeout: float | None = 300):
        return super().initialize(timeout=timeout)

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
