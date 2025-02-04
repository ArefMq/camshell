import platform
import click

from camshell.camshell_core import CamShell
from camshell.display.curses_screen import CursesScreen, CursesScreenImproved
from camshell.display.ui_screen import UIScreen
from camshell.vision import FakeCamera
from camshell.vision.camera import MacosCamera


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
    try:
        # camera = FakeCamera(cap_id)
        camera = MacosCamera(device_index=0, max_rate=5)
        
        # display = UIScreen()
        display = CursesScreenImproved()
        
        cs = CamShell(camera, display)
        cs.initialize()
        cs.run()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    cli()
