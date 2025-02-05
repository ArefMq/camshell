import threading

from loguru import logger

from camshell.interfaces import Camera, Display, Size


class CamShell:
    def __init__(
        self,
        camera: Camera,
        display: Display,
        refresh_rate: float = 0.1,
    ) -> None:
        self.camera = camera
        self.display = display
        self.__refresh_rate = refresh_rate
        self.__shutdown_event = threading.Event()

    @property
    def size(self) -> Size:
        return self.display.get_size()

    def initialize(self) -> None:
        self.camera.initialize()
        self.display.initialize()
        self.camera.optimize_for(self.size)

    def finalize(self) -> None:
        self.camera.finalize()
        self.display.finalize()

    def render(self) -> None:
        try:
            image = self.camera.read()
            self.display.render(image)
        except RuntimeError as e:
            logger.error(f"Failed to read frame: {e}")

    def run(self) -> None:
        try:
            self.__shutdown_event.clear()
            while not self.__shutdown_event.wait(self.__refresh_rate):
                self.render()
        finally:
            self.finalize()

    def stop(self) -> None:
        self.__shutdown_event.set()

    @classmethod
    def start(cls, **kwargs) -> None:
        from camshell.display import Display
        from camshell.vision.camera import GenericCamera

        camera = GenericCamera(**kwargs)
        display = Display()
        cls = cls(camera, display)
        cls.run()
