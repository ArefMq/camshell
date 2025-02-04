# Initializes the GStreamer library and the GObject and GLib modules.
import gi

gi.require_version("GLib", "2.0")
gi.require_version("GObject", "2.0")
gi.require_version("Gst", "1.0")

from gi.repository import GLib, Gst  # noqa: E402, F401

Gst.init(None)


def monotonic_time() -> float:
    return GLib.get_monotonic_time() * 1e-6