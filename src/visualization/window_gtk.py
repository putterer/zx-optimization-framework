import os
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk


# https://python-gtk-3-tutorial.readthedocs.io/en/latest/objects.html

class WindowGTK:
    def __init__(self):
        self.window: Gtk.Window = None
        self.handler: WindowGTK.EventHandler = None
        self.canvas: Gtk.DrawingArea = None

        self.window = self.init_window()

    def init_window(self) -> Gtk.Window:
        os.environ["GTK_THEME"] = "theme:adwaita" # light theme

        builder = Gtk.Builder()
        builder.add_from_file("layout.glade")

        self.handler = WindowGTK.EventHandler()
        builder.connect_signals(self.handler)

        window = builder.get_object("mainWindow")

        window.show_all()

        return window

    def main_loop(self):
        Gtk.main()

    class EventHandler:
        def onCursorButtonClicked(self, button):
            print("hello world")

        def onDestroy(self, *args):
            Gtk.main_quit()
            sys.exit(0)
