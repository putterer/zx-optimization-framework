import math

import gi
from graph_tool import VertexPropertyMap

from zxopt.util import is_interactive
from zxopt.visualization.window import Window

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
    diagram_width: int
    diagram_height: int

    def __init__(self, diagram: Diagram, width: int = 500, height: int = 300, diagram_width=400, diagram_height=250):
        super().__init__(width, height)
        self.diagram = diagram
        self.diagram_width = diagram_width
        self.diagram_height = diagram_height

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
                phase = str(round(self.diagram.phase_prop[v] / math.pi * 100.0) / 100.0) if self.diagram.phase_prop[v] != 0.0 else ""
                # if phase == "1.0":
                #     phase = "π"
                vertex_labels[v] = phase
                if self.diagram.vertex_type_prop[v] == VERTEX_SPIDER_GREEN:
                    vertex_fill_colors[v] = GREEN_SPIDER_COLOR
                else:
                    vertex_fill_colors[v] = RED_SPIDER_COLOR

        edge_colors = g.new_edge_property("string")
        for e in g.edges():
            edge_colors[e] = HADMARAD_EDGE_COLOR if self.diagram.hadamard_prop[e] else EDGE_COLOR

        # vertex positions
        vertex_pos = self.calculate_vertex_positons()

        graph_draw(g,
                   pos = vertex_pos,
                   vertex_text = vertex_labels,
                   vertex_fill_color = vertex_fill_colors,
                   vertex_color = VERTEX_BORDER_COLOR,
                   vertex_size = 20,
                   edge_color = edge_colors,
                   output_size = (self.diagram_width, self.diagram_height),
                   output = filename,
                   fmt = "svg",
                   bg_color = to_cairo_color("#FFFFFF") if is_interactive() else None,
                   inline = False,
                   )

    def calculate_vertex_positons(self) -> VertexPropertyMap:
        diagram = self.diagram
        g = diagram.g

        pos = g.new_vertex_property("vector<double>")

        inputs = diagram.get_inputs()
        outputs = diagram.get_outputs()
        spiders = diagram.get_spiders()

        SPACING = 100 # TODO: move

        to_process = []

        for v in g.vertices():
            pos[v] = [0, 0] # TODO: what does "vector" type mean?

        for input in inputs:
            pos[input] = [0, SPACING * diagram.get_boundary_index(input)]
            to_process.append(input)

        # TODO: alignment algorithm
        # while len(to_process) > 0:
        #
        # #


        return pos



### Test
if __name__ == "__main__":
    diagram = Diagram()
    in1 = diagram.add_boundary("in")
    in2 = diagram.add_boundary("in")
    out1 = diagram.add_boundary("out")
    out2 = diagram.add_boundary("out")

    s1_1 = diagram.add_spider(0.0, "green")
    s1_2 = diagram.add_spider(0.0, "red")
    s2_1 = diagram.add_spider(math.pi, "red")

    diagram.add_wire(in1, s1_1)
    diagram.add_wire(in2, s1_2)
    diagram.add_wire(s1_1, s1_2)
    diagram.add_wire(s1_1, s2_1)
    diagram.add_wire(s2_1, out1)
    diagram.add_wire(s1_2, out2)

    renderer = DiagramRenderer(diagram)

    window = Window(renderer)
    window.main_loop()
