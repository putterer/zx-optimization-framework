import math
from typing import Set, Optional

import gi
from graph_tool import VertexPropertyMap, Vertex

from zxopt.util import is_interactive

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
HADAMARD_EDGE_COLOR = "#4444DD"

TEMP_SVG_FILENAME = "diagram_render.svg"

DIAGRAM_RENDER_OFFSET = [30, 30]
DIAGRAM_RENDER_SPACING = 70
DIAGRAM_INPUT_GRAB_SCALE = 0.80

class DiagramRenderer(Renderer):
    diagram: Diagram
    diagram_width: int
    diagram_height: int
    disable_alignment: bool

    vertex_pos: Optional[VertexPropertyMap]
    grabbed_vertex: Optional[Vertex]

    def __init__(self, diagram: Diagram, width: int = 500, height: int = 300, diagram_width=800, diagram_height=600, disable_alignment=False):
        super().__init__(width, height)
        self.diagram = diagram
        self.diagram_width = diagram_width
        self.diagram_height = diagram_height
        self.disable_alignment = disable_alignment

        self.vertex_pos = None
        self.grabbed_vertex = None

    # def on_resize(self):
    #     super().on_resize()
    #     self.diagram_width = self.drawing_area.get_allocated_width()
    #     self.diagram_height = self.drawing_area.get_allocated_height()

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
                #     phase = "??"
                vertex_labels[v] = phase
                if self.diagram.vertex_type_prop[v] == VERTEX_SPIDER_GREEN:
                    vertex_fill_colors[v] = GREEN_SPIDER_COLOR
                else:
                    vertex_fill_colors[v] = RED_SPIDER_COLOR

        edge_colors = g.new_edge_property("string")
        for e in g.edges():
            edge_colors[e] = HADAMARD_EDGE_COLOR if self.diagram.hadamard_prop[e] else EDGE_COLOR

        # vertex positions
        if not self.disable_alignment:
            if self.vertex_pos is None:
                self.vertex_pos = self.calculate_vertex_positons()

            vertex_pos = self.vertex_pos
        else:
            vertex_pos = None

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
                   bg_color = to_cairo_color("#FFFFFF") if is_interactive() else to_cairo_color("#FFFFFF"),
                   inline = False,
                   fit_view=False,
                   fit_view_ink=False,
                   adjust_aspect=False
                   )

    def calculate_vertex_positons(self) -> VertexPropertyMap:
        diagram = self.diagram
        g = diagram.g

        pos = g.new_vertex_property("vector<double>")
        for v in g.vertices():
            pos[v] = [400, 400]

        inputs = diagram.get_inputs()
        outputs = diagram.get_outputs()
        spiders = diagram.get_spiders()

        # Alignment algorithm see notes
        # BFS
        processed: Set[Vertex] = set()
        to_process: Set[Vertex] = set()

        for input in inputs:
            pos[input] = [diagram.get_boundary_index(input) + DIAGRAM_RENDER_OFFSET[0], DIAGRAM_RENDER_SPACING * diagram.get_boundary_index(input) + DIAGRAM_RENDER_OFFSET[1]]

            processed.add(input)
            for n in input.all_neighbors():
                to_process.add(n)

        # alignment algorithm
        current_step = 1
        last_step_skipped = False
        while len(to_process) > 0:

            # if to process only contains outputs, place them
            if all([diagram.is_output(v) for v in to_process]):
                for output in to_process:
                    pos[output] = [DIAGRAM_RENDER_SPACING * current_step + DIAGRAM_RENDER_OFFSET[0], DIAGRAM_RENDER_SPACING * diagram.get_boundary_index(output) + DIAGRAM_RENDER_OFFSET[1]]

                to_process.clear()
                break

            could_be_placed = set()
            # for qubit_index in range(len(diagram.get_inputs())):
            #     for spider in to_process:
            #         if diagram.get_spider_qubit_index(spider) == qubit_index:
            #             could_be_placed.add(spider)
            #             break

            # iterate over all canidates, only place if all other neighbors can also get placed
            for vertex in [v for v in to_process if diagram.is_spider(v)]:
                if vertex in could_be_placed: # skip vertex if already in placement due to neighbor getting placed
                    continue

                vertex_qubit_index = diagram.get_spider_qubit_index(vertex)
                if len([v for v in could_be_placed if diagram.get_spider_qubit_index(v) == vertex_qubit_index]) == 0: # ensure there is no spider getting placed on this qubit already
                    non_placed_neighbors = [v for v in vertex.all_neighbors() if v not in could_be_placed and v not in processed and diagram.is_spider(v)]
                    non_placed_other_qubit_neighbors = [v for v in non_placed_neighbors if diagram.get_spider_qubit_index(v) != vertex_qubit_index]
                    # those nodes could also have neighbors, but let's ignore them for now

                    all_placeable = True
                    for neighbor in non_placed_other_qubit_neighbors:
                        neighbor_qubit_index = diagram.get_spider_qubit_index(neighbor)
                        if len([v for v in could_be_placed if diagram.get_spider_qubit_index(v) == neighbor_qubit_index]) != 0: # ensure there is no spider getting placed on this qubit already
                            if neighbor not in to_process and not last_step_skipped: # this will block placement till this one has been discovered via a different route, gets disabled after a placement fail
                                all_placeable = False
                                break

                    if all_placeable:
                        could_be_placed.add(vertex)
                        for n in non_placed_other_qubit_neighbors:
                            could_be_placed.add(n)

            if len(could_be_placed) == 0:
                last_step_skipped = True
                continue
            else:
                last_step_skipped = False

            # place spiders
            for spider in could_be_placed:
                pos[spider] = [DIAGRAM_RENDER_SPACING * current_step + DIAGRAM_RENDER_OFFSET[0], DIAGRAM_RENDER_SPACING * diagram.get_spider_qubit_index(spider) + DIAGRAM_RENDER_OFFSET[1]]

                if spider in to_process:
                    to_process.remove(spider)

                processed.add(spider)
                for neighbor in [v for v in spider.all_neighbors() if not v in processed and not v in to_process and not v in could_be_placed]:
                    to_process.add(neighbor)

            # TODO: break loops in case something goes wrong
            current_step += 1

        return pos

    def mouse_moved(self, x: int, y: int):
        x *= DIAGRAM_INPUT_GRAB_SCALE
        y *= DIAGRAM_INPUT_GRAB_SCALE

        if self.grabbed_vertex is not None:
            self.vertex_pos[self.grabbed_vertex] = [x - (x % 10), y - (y % 10)]
            self.drawing_area.queue_draw()


    def mouse_pressed(self, x: int, y: int, button: int):
        x *= DIAGRAM_INPUT_GRAB_SCALE
        y *= DIAGRAM_INPUT_GRAB_SCALE

        # find closest vertex
        closest_vertex, closest_dist_squared = (None, 1000000)
        for v in self.diagram.g.vertices():
            dist_squared = (self.vertex_pos[v][0] - x)**2 + (self.vertex_pos[v][1] - y)**2
            if dist_squared < closest_dist_squared:
                closest_dist_squared = dist_squared
                closest_vertex = v

        if closest_dist_squared < 150**2:
            self.grabbed_vertex = closest_vertex

    def mouse_released(self, x: int, y: int, button: int):
        x *= DIAGRAM_INPUT_GRAB_SCALE
        y *= DIAGRAM_INPUT_GRAB_SCALE

        self.grabbed_vertex = None
        self.drawing_area.queue_draw()
