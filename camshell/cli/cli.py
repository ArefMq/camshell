import platform

import click

from camshell import CamShell
from camshell.display import Display
from camshell.vision.camera import GenericCamera


DEFAULT_ARGS = {
    "device_index": 0,
    "source": "avf" if platform.system() == "Darwin" else "v4l2",
    "max_rate": 20,
}


def __parse_arguments(arguments: str) -> dict:
    """
    gets something like: "key1=value1,key2=value2"
    return {"key1": "value1", "key2": "value2"}
    """
    if arguments is None:
        return {}
    return dict([arg.split("=") for arg in arguments.strip().split(",")])


@click.command()
@click.argument("cap_id", type=str, default=None, required=False)
@click.argument("arguments", type=str, default=None, required=False)
@click.option(
    "-f",
    "--file",
    help="Use file source instead of camera stream.",
)
def cli(cap_id: str | None, arguments: str | None, file: str | None) -> None:
    """
    A Simple CLI to display video feed in terminal.
    """

    args = DEFAULT_ARGS | {**__parse_arguments(arguments)}

    if file is None:  # Reading from Video Source
        if cap_id is not None:
            args["device_index"] = cap_id
    else:  # Reading from File
        args["source"] = "file"
        args["file_path"] = file

    try:
        camera = GenericCamera(**args)
        display = Display(frame_time_limit=1/30)

        cs = CamShell(camera, display)
        cs.initialize()
        cs.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli()
