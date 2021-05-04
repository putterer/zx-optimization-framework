import math
from io import BytesIO

import cairo
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from zxopt.util import Loggable, display_in_notebook

# https://www.tutorialspoint.com/pygtk/pygtk_drawingarea_class.htm

class Renderer(Loggable):

    def __init__(self, drawing_area: Gtk.DrawingArea = None, width: int = 500, height: int = 300):
        super().__init__()

        self.drawing_area: Gtk.DrawingArea = drawing_area
        self.width: int = width
        self.height: int = height

        if drawing_area is not None:
            self.on_resize()
            drawing_area.connect("size-allocate", lambda widget, allocation: self.on_resize())
            drawing_area.connect("draw", self.on_render_requested)
        else:
            pass

    # render requested by drawing area
    def on_render_requested(self, drawing_area: Gtk.Widget, cr: cairo.Context):
        self.render(cr)

    def on_resize(self):
        if self.width == self.drawing_area.get_allocated_width() and self.height == self.drawing_area.get_allocated_height():
            return

        self.width = self.drawing_area.get_allocated_width()
        self.height = self.drawing_area.get_allocated_height()
        self.log.info(f"Resized to {self.width}x{self.height}")

    def request_render(self):
        if self.drawing_area is not None:
            self.drawing_area.queue_draw()

    def render_image(self):
        svg_io = BytesIO()
        with cairo.SVGSurface(svg_io, self.width, self.height) as surface:
            context = cairo.Context(surface)
            self.render(context)

        display_in_notebook(svg_io)


    def render(self, cr: cairo.Context):
        self.render_test(cr)

    def render_test(self, cr: cairo.Context):
        for x in range(0, 10):
            for y in range(0, 10):
                cr.set_source_rgb(1.0, 0.5, 0.0)
                cr.arc(x * 40 + 50, y * 40 + 40, 18, 0, 2*math.pi)
                cr.fill()


