from camshell.interfaces import Camera, Image, Size
from camshell.vision import gstream_components as components
from camshell.vision.gstream_pipeline import GStreamerPipeline


class GenericCamera(GStreamerPipeline, Camera):
    def __init__(self, avf_source: bool = False, **kwargs):
        super().__init__()
        video_source = (
            components.AVFVideoSource(kwargs)
            if avf_source
            else components.V4L2Source(kwargs)
        )
        self.pipeline_description = (
            video_source
            + components.VideoRate(kwargs)
            + components.VideoConvert(kwargs)
            + components.Queue()
            + components.AppSink()
        )
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
