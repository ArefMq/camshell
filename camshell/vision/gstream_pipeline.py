import threading
from abc import ABC

from loguru import logger

from camshell.vision.__gi import GLib, Gst
from camshell.vision.gstream_components import GStreamComponent


class GStreamerPipeline(ABC):
    def __init__(self):
        self.pipeline_description: str | GStreamComponent | None = None
        self.pipeline: Gst.Pipeline | None = None
        # self.__cap_write_lock = GLib.Mutex()
        self.lock = threading.Lock()
        self.__buffer_caps: tuple[Gst.Buffer, Gst.Caps] | None = None
        self.__first_sample = threading.Event()

    def on_new_sample(self, sink: Gst.Element) -> Gst.FlowReturn:
        try:
            sample = sink.emit("pull-sample")
            if sample:
                buffer = sample.get_buffer()
                caps = sample.get_caps()
                with self.lock:
                    self.__buffer_caps = (buffer, caps)
                    self.__first_sample.set()
            return Gst.FlowReturn.OK
        except Exception as e:
            logger.error(f"Error on new sample: {e}")
            return Gst.FlowReturn.ERROR

    @property
    def buffer(self) -> Gst.Buffer | None:
        return self.__buffer_caps[0] if self.__buffer_caps is not None else None

    @property
    def caps(self) -> Gst.Caps | None:
        return self.__buffer_caps[1] if self.__buffer_caps is not None else None

    # @property
    # @contextmanager
    # def lock(self):
    #     try:
    #         self.__cap_write_lock.lock()
    #         yield self.__cap_write_lock
    #     finally:
    #         self.__cap_write_lock.unlock()

    def create_pipeline(self) -> None:
        """
        Create a GStreamer pipeline from the pipeline-description.
        Overwrite this method to create a custom pipeline without providing a
        pipeline-description.
        """
        assert self.pipeline_description is not None, "Pipeline description is not set"

        self.pipeline = Gst.parse_launch(str(self.pipeline_description))
        assert self.pipeline is not None, "Pipeline is failed to create"

        app_sink = self.pipeline.get_by_name("appsink")
        assert app_sink is not None, "App sink is not found"

        app_sink.set_property("emit-signals", True)
        app_sink.connect("new-sample", self.on_new_sample)

        # connect bus
        bus = self.pipeline.get_bus()
        bus.add_signal_watch()
        bus.connect("message::eos", self._on_eos)
        bus.connect("message::error", self._on_error)

    def _on_eos(self, message: Gst.Message) -> None:
        logger.error(f"End of stream: {message.src.name}")

    def _on_error(self, message: Gst.Message) -> None:
        err, debug = message.parse_error()
        logger.error(f"Error: {err} - {debug}")

    def start_pipeline(self) -> None:
        logger.info("Starting the pipeline")
        assert self.pipeline is not None, "Pipeline has not been created"
        self.pipeline.set_state(Gst.State.PLAYING)

    def initialize(
        self,
        description: str | GStreamComponent | None = None,
        timeout: float | None = 300,
    ) -> None:
        if description:
            self.pipeline_description = description
        logger.info("Initializing GStreamer pipeline")
        try:
            self.create_pipeline()
        except Exception as exp:
            logger.error(f"Failed to create pipeline: {exp}")
            raise RuntimeError("Failed to create pipeline") from exp
        try:
            self.start_pipeline()
        except Exception as exp:
            raise RuntimeError("Failed to start pipeline") from exp
        logger.success("Pipeline created")
        if timeout is not None:
            logger.info("Waiting for the first sample")
            if self.__first_sample.wait(timeout):
                logger.success("First sample received")
            else:
                raise TimeoutError("Timeout waiting for the first sample")

    def finalize(self) -> None:
        if self.pipeline:
            logger.info("Stopping the pipeline")
            self.pipeline.set_state(Gst.State.NULL)

    @classmethod
    def list_devices(self):
        logger.info("Listing GStreamer devices")
        devices = Gst.Device.monitor_get_devices()
        for device in devices:
            logger.info(f"Device: {device.get_display_name()}")
        logger.success("Devices listed")
