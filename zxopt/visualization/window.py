import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from zxopt.visualization.renderer import Renderer

# https://python-gtk-3-tutorial.readthedocs.io/en/latest/objects.html

LAYOUT_FILE = "layout.glade"

class Window:
    window: Gtk.Window
    drawing_area: Gtk.DrawingArea
    renderer: Renderer

    def __init__(self, renderer: Renderer = Renderer()):
        self.window = self.init_window()
        self.renderer = renderer
        renderer.set_drawing_area(self.drawing_area)

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

        self.window.connect("motion_notify_event", self.mouse_moved)
        self.window.connect("button_press_event", self.mouse_pressed)
        self.window.connect("button_release_event", self.mouse_released)

    def main_loop(self):
        Gtk.main()



    # Signal handlers

    def mouse_moved(self, widget, event):
        self.renderer.mouse_moved(event.x, event.y)

    def mouse_pressed(self, widget, event):
        self.renderer.mouse_pressed(event.x, event.y, event.button)

    def mouse_released(self, widget, event):
        self.renderer.mouse_released(event.x, event.y, event.button)

    def on_tool_button_clicked(self, button: Gtk.Button):
        print("hello world ", button.get_label())

    def on_destroy(self, *args):
        Gtk.main_quit()
        # sys.exit(0)

    def on_window_reconfigure(self, *args):
        pass
