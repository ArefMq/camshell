import platform
import click
from .xdisplay import XDisplay


@click.command()
@click.argument("cap_id", type=str, default=None, required=False)
def cli(cap_id: str | None):
    """
    A Simple CLI to display video feed in terminal.

    Arguments:
    cap_id -- Camera ID or path to video device.
    """
    if cap_id is None:
        cap_id = 0 if platform.system() == "Darwin" else "/dev/video0"
    XDisplay.start(cap_id)


if __name__ == "__main__":
    cli()
