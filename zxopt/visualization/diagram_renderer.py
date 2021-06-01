import math

import gi

gi.require_version('Rsvg', '2.0')
from gi.repository import Rsvg

import cairo
from graph_tool.draw import graph_draw

from zxopt.data_structures.diagram.diagram import VERTEX_BOUNDARY, INPUT, VERTEX_SPIDER_GREEN, Diagram
from zxopt.visualization.render_util import to_cairo_color
from zxopt.visualization.renderer import Renderer

GREEN_SPIDER_COLOR = "#96FAAA"
RED_SPIDER_COLOR = "#FF9191"
BOUNDARY_COLOR = "#BBBBBB"
VERTEX_BORDER_COLOR = "#333333"

EDGE_COLOR = "#444444"
HADMARAD_EDGE_COLOR = "#4444DD"

TEMP_SVG_FILENAME = "diagram_render.svg"

class DiagramRenderer(Renderer):
    diagram: Diagram

    def __init__(self, diagram: Diagram, width: int = 500, height: int = 300):
        super().__init__(width, height)
        self.diagram = diagram

    def render(self, ctx: cairo.Context):
        self.render_to_image(TEMP_SVG_FILENAME)

        # source_surface = cairo.SVGSurface.create_from_png(TEMP_PNG_FILENAME)
        # ctx.set_source_surface(source_surface)
        # ctx.paint()

        handle = Rsvg.Handle()
        svg = handle.new_from_file(TEMP_SVG_FILENAME)
        svg.render_cairo(ctx)

        # os.remove(TEMP_PNG_FILENAME)

    # https://graph-tool.skewed.de/static/doc/draw.html#graph_tool.draw.graph_draw
    def render_to_image(self, filename: str):
        g = self.diagram.g

        vertex_labels = g.new_vertex_property("string")
        vertex_fill_colors = g.new_vertex_property("string")
        for v in g.vertices():
            if self.diagram.vertex_type_prop[v] == VERTEX_BOUNDARY:
                vertex_labels[v] = "I" if self.diagram.boundary_type_prop[v] == INPUT else "O"
                vertex_fill_colors[v] = BOUNDARY_COLOR
            else:
                vertex_labels[v] = str(round(self.diagram.phase_prop[v] / math.pi * 100.0) / 100.0) if self.diagram.phase_prop[v] != 0.0 else ""
                if self.diagram.vertex_type_prop[v] == VERTEX_SPIDER_GREEN:
                    vertex_fill_colors[v] = GREEN_SPIDER_COLOR
                else:
                    vertex_fill_colors[v] = RED_SPIDER_COLOR

        edge_colors = g.new_edge_property("string")
        for e in g.edges():
            edge_colors[e] = HADMARAD_EDGE_COLOR if self.diagram.hadamard_prop[e] else EDGE_COLOR

        graph_draw(g,
                   vertex_text = vertex_labels,
                   vertex_fill_color = vertex_fill_colors,
                   vertex_color = VERTEX_BORDER_COLOR,
                   vertex_size = 20,
                   edge_color = edge_colors,
                   output_size = (self.width, self.height),
                   output = filename,
                   fmt = "svg",
                   bg_color = to_cairo_color("#FFFFFF"),
                   inline = False
                   )