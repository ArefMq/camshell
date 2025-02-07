# CamShell

CamShell, a light weight ASCII art video streamer.

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

# Or stream from a file
camshell -f ./my_video.mp4
```

## Python API Usage

If you’d like to use CamShell in your Python code, here’s how:

```python
from camshell import CamShell

# simply call:
device_id = "/dev/video0"
CamShell.start(device_index=device_id)

# or in case of MacOS
CamShell.start(avf_source=True)
```

Run on a custom screen

```python
from camshell import CamShell
from camshell.display import Display
from camshell.vision.camera import GenericCamera

# Create a GStream-based camera object
camera = GenericCamera(device_index=cap_id, avf_source=True)

# Create a Curses display
display = Display()

# Create and run the CamShell
cs = CamShell(camera, display)
cs.initialize()
cs.run()
```

## Output Example

![Example Output](https://github.com/ArefMq/camshell/blob/main/docs/screenshot_shrek.png)

[![](https://markdown-videos-api.jorgenkh.no/youtube/erU1So2IP7E)](https://youtu.be/erU1So2IP7E)