from dataclasses import dataclass, field
from typing import Union


@dataclass
class GStreamComponent:
    component: str
    arguments: dict[str, str] = field(default_factory=dict)
    default_args: dict[str, str] = field(default_factory=dict)

    def __post_init__(self):
        self.arguments = self.default_args | self.arguments

    def __str__(self) -> str:
        return self.format()

    def format(self) -> str:
        return self.component.format(**self.arguments)

    def __add__(self, other: Union[str, "GStreamComponent"]) -> "GStreamComponent":
        if isinstance(other, str):
            return GStreamComponent(self.component + " ! " + other, self.arguments)
        return GStreamComponent(
            self.component + " ! " + other.component,
            {**self.arguments, **other.arguments},
        )

    def __radd__(self, other: str) -> "GStreamComponent":
        return GStreamComponent(other + " ! " + self.component, self.arguments)

    def __iadd__(self, other: Union[str, "GStreamComponent"]) -> "GStreamComponent":
        if isinstance(other, str):
            self.component += " ! " + other
        else:
            self.component += " ! " + other.component
            self.arguments.update(other.arguments)
        return self


class V4L2Source(GStreamComponent):
    def __init__(self, arguments: dict[str, str]):
        super().__init__(
            "v4l2src device={device_index}",
            arguments,
            {"device_index": "/dev/video0"},
        )


class AVFVideoSource(GStreamComponent):
    def __init__(self, arguments: dict[str, str]):
        super().__init__(
            "avfvideosrc device-index={device_index}",
            arguments,
            {"device_index": "0"},
        )


class FileSource(GStreamComponent):
    def __init__(self, arguments: dict[str, str]):
        super().__init__(
            "filesrc location={file_path} ! decodebin",
            arguments,
        )


class VideoRaw(GStreamComponent):
    def __init__(self, arguments: dict[str, str]):
        super().__init__(
            "video/x-raw, format=(string){format}, width=(int){width}, height=(int){height}, framerate=(fraction){framerate}",
            arguments,
            {
                "format": "BGR",
                "width": "640",
                "height": "480",
                "framerate": "30/1",
            },
        )


class VideoConvert(GStreamComponent):
    def __init__(self, arguments: dict[str, str]):
        super().__init__(
            "videoconvert ! video/x-raw, format={output_format}",
            arguments,
            {"output_format": "BGR"},
        )


class VideoRate(GStreamComponent):
    def __init__(self, arguments: dict[str, str], direct: bool = True):
        if direct:
            raw = "videorate max-rate={max_rate}"
            default_args = {"max_rate": "30"}
        else:
            raw = "videorate ! video/x-raw,framerate={max_rate}"
            default_args = {"max_rate": "30/1"}

        super().__init__(raw, arguments, default_args)


@dataclass
class Queue(GStreamComponent):
    def __init__(self):
        super().__init__("queue")


@dataclass
class AppSink(GStreamComponent):
    def __init__(self):
        super().__init__("appsink name=appsink")


if __name__ == "__main__":
    args = {
        "device_index": "0",
        "format": "BGR",
        "width": "640",
        "height": "480",
        "framerate": "30/1",
        "output_format": "BGR",
    }

    print(
        str(
            AVFVideoSource(arguments=args)
            + VideoRaw(arguments=args)
            + VideoConvert(arguments=args)
            + Queue()
            + AppSink()
        )
    )
