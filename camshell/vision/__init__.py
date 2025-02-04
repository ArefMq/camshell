from loguru import logger
from camshell.interfaces import Camera, Image, Size
import cv2
import random

class FakeCamera(Camera):
    def __init__(self, cap_id: str):
        self.cap_id = cap_id
        self.size = Size(width=640, height=480)
        self.cap_id = cap_id

    def optimize_for(self, size: Size) -> None:
        self.size = size

    def initialize(self) -> None:
        # self.cap = cv2.VideoCapture(self.cap_id)
        logger.success(f"Camera initialized with ID: {self.cap_id}")

    def read(self) -> Image:
        random_image = bytearray()
        random_image.extend(random.randint(0, 255) for _ in range(self.size.width * self.size.height * 3))
        return Image(random_image, self.size)
        # ret, frame = self.cap.read()
        # if not ret:
        #     raise RuntimeError("Failed to read frame")
        # resized = cv2.resize(frame, (self.size.width, self.size.height))
        # return Image(resized.tobytes(), self.size)
