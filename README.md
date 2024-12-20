# CamShell

CamShell, A simple way to stream a camera as ASCII art directly in a terminal.


## Installation

Using pip:

```bash
pip install camshell
```

## How to Use

CLI Usage:

After installation, you can run the `camshell` command-line tool or by providing
the device id.

```bash
# Run the default device
camshell

# Or run by device-id
camshell 1

# Or a device path specifically
camshell /dev/video3
```

## Python API Usage

If you’d like to use XDisplay in your Python code, here’s how:

```python
from camshell.xdisplay import XDisplay as CamShellDisplay

# simply call:
device_id = "/dev/video0"
CamShellDisplay.start(device_id)
```

Run on a custom screen

```python
from asciimatics.screen import Screen
from camshell.xdisplay import XDisplay as CamShellDisplay

with XDisplay(cap_id="/dev/video0") as display:
    Screen.wrapper(display.run)
```
