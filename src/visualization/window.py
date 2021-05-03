import os
import sys

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from src.visualization import Renderer

# https://python-gtk-3-tutorial.readthedocs.io/en/latest/objects.html

LAYOUT_FILE = "layout.glade"

class Window:
    def __init__(self):
        self.window: Gtk.Window = None
        self.drawing_area: Gtk.DrawingArea = None
        self.renderer: Renderer = None

        self.window = self.init_window()
        self.renderer = Renderer(self.drawing_area)

        self.connect_signals()

    def init_window(self) -> Gtk.Window:
        os.environ["GTK_THEME"] = "theme:adwaita"  # light theme

        builder = Gtk.Builder()

        if os.path.isfile(LAYOUT_FILE):
            builder.add_from_file(LAYOUT_FILE)
        else:
            builder.add_from_file(os.path.join("../", LAYOUT_FILE))

        window = builder.get_object("mainWindow")
        self.drawing_area = builder.get_object("mainDrawingArea")

        builder.connect_signals(self)  # connect all signals specified in glade

        window.show_all()

        return window

    def connect_signals(self):
        self.window.connect("destroy",
                            self.on_destroy)  # would also be hooked by builder.connect_signals -> onDestroy()

        self.window.connect("configure-event", self.on_window_reconfigure)

    def main_loop(self):
        Gtk.main()



    # Signal handlers

    def on_tool_button_clicked(self, button: Gtk.Button):
        print("hello world ", button.get_label())

    def on_destroy(self, *args):
        Gtk.main_quit()
        sys.exit(0)

    def on_window_reconfigure(self, *args):
        pass
