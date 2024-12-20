from time import sleep
import cv2
from asciimatics.screen import Screen, _CursesScreen
from asciimatics.exceptions import ResizeScreenError


class XDisplay:
    def __init__(self, cap_id: int | str) -> None:
        self.screen: _CursesScreen = None
        self.cap_id: int | str = cap_id
        self.cap: cv2.VideoCapture = None

    def get_image(self) -> cv2.UMat:
        ret, frame = self.cap.read()
        if not ret:
            raise ValueError("Error: Could not read frame.")
        return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    def image_2_text(self, image: cv2.UMat | list[list[int]]) -> list[str]:
        return ["".join([" .:-=+*#%@"[pixel // 32] for pixel in row]) for row in image]

    def render(self, width: int, height: int) -> None:
        image = self.get_image()
        resized_frame = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        text_image = self.image_2_text(resized_frame)
        self.display(text_image)

    def display(self, str_mat: list[str]) -> None:
        self.screen.clear_buffer(7, 0, 0)
        for i, row in enumerate(str_mat):
            self.screen.print_at(row, 0, i, colour=7)
        self.screen.refresh()

    def run(self, screen: _CursesScreen) -> None:
        self.screen = screen
        while True:
            try:
                term_height, term_width = screen.dimensions
                self.render(int(term_width), int(term_height))
            except ResizeScreenError:
                pass
            except KeyboardInterrupt:
                break
            sleep(0.1)

    def __enter__(self) -> "XDisplay":
        cap = cv2.VideoCapture(self.cap_id)
        if not cap.isOpened():
            raise ValueError("Error: Could not open video device.")
        self.cap = cap
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.cap.release()
        cv2.destroyAllWindows()

    @classmethod
    def start(cls, cap_id: int | str) -> None:
        try:
            cap_id = int(cap_id)
        except ValueError:
            pass

        with cls(cap_id=cap_id) as x:
            Screen.wrapper(x.run)
