from typing import Optional, List

import numpy as np
from graph_tool import Graph, VertexPropertyMap, Vertex, Edge, EdgePropertyMap

VERTEX_BOUNDARY = "BOUNDARY"
VERTEX_SPIDER_GREEN = "SPIDER_GREEN"
VERTEX_SPIDER_RED = "SPIDER_RED"
SPIDER_COLOR_TO_VERTEX_TYPE = {"green": VERTEX_SPIDER_GREEN, "red": VERTEX_SPIDER_RED}
VERTEX_TYPE_TO_SPIDER_COLOR = {SPIDER_COLOR_TO_VERTEX_TYPE[c]: c for c in SPIDER_COLOR_TO_VERTEX_TYPE}

SPIDER_COLORS = {"green", "red"}
OTHER_SPIDER_COLOR = {"red": "green", "green": "red"}

INPUT = "IN"
OUTPUT = "OUT"
BOUNDARY_NAME_TO_TYPE = {"in": INPUT, "out": OUTPUT, "IN": INPUT, "OUT": OUTPUT}

class Diagram:
    g: Graph
    vertex_type_prop: VertexPropertyMap
    vertex_identifier_prop: VertexPropertyMap  # removing vertices invalidates the identifiers from graph_tool -> assign ourselves
    phase_prop: VertexPropertyMap
    hadamard_prop: EdgePropertyMap
    boundary_type_prop: VertexPropertyMap
    boundary_qubit_indices_prop: VertexPropertyMap
    spider_qubit_indices_prop: VertexPropertyMap

    def __init__(self, g: Graph = None):
        g = (g if g is not None else Graph(directed=False)) # what the heck python, default constructor parameters are only evaluated once
        self.g = g

        if not "vertex_type_prop" in self.g.vertex_properties:
            self.vertex_type_prop = g.new_vertex_property("string")
            self.vertex_identifier_prop = g.new_vertex_property("string")
            self.phase_prop = g.new_vertex_property("float")
            self.hadamard_prop = g.new_edge_property("bool")
            self.boundary_type_prop = g.new_vertex_property("string")
            self.boundary_qubit_indices_prop = g.new_vertex_property("int")
            self.spider_qubit_indices_prop = g.new_vertex_property("int")

            self.g.vertex_properties["vertex_type_prop"] = self.vertex_type_prop # internal property map, is included in copy() for cloning
            self.g.vertex_properties["vertex_identifier_prop"] = self.vertex_identifier_prop
            self.g.vertex_properties["phase_prop"] = self.phase_prop
            self.g.edge_properties["hadamard_prop"] = self.hadamard_prop
            self.g.vertex_properties["boundary_type_prop"] = self.boundary_type_prop
            self.g.vertex_properties["boundary_qubit_indices_prop"] = self.boundary_qubit_indices_prop
            self.g.vertex_properties["spider_qubit_indices_prop"] = self.spider_qubit_indices_prop

        else:
            self.vertex_type_prop = self.g.vertex_properties["vertex_type_prop"]
            self.vertex_identifier_prop = self.g.vertex_properties["vertex_identifier_prop"]
            self.phase_prop = self.g.vertex_properties["phase_prop"]
            self.hadamard_prop = self.g.edge_properties["hadamard_prop"]
            self.boundary_type_prop = self.g.vertex_properties["boundary_type_prop"]
            self.boundary_qubit_indices_prop = self.g.vertex_properties["boundary_qubit_indices_prop"]
            self.spider_qubit_indices_prop = self.g.vertex_properties["spider_qubit_indices_prop"]


    def add_spider(self, phase: float = 0.0, color: str = "green", origin_qubit_index: int = None, identifier: str = None) -> Vertex:
        v = self.g.add_vertex()
        self.vertex_type_prop[v] = SPIDER_COLOR_TO_VERTEX_TYPE[color]
        self.phase_prop[v] = np.mod(phase, np.pi * 2.0)

        if origin_qubit_index:
            self.spider_qubit_indices_prop[v] = origin_qubit_index
        if identifier:
            self.vertex_identifier_prop[v] = identifier

        return v

    def remove_spiders(self, vertices: List[Vertex]):
        self.g.remove_vertex(vertices)

    """
    Removes a single spider from the diagram, this will invalidate other spiders!
    
    "Because of this, the only safe way to remove more than one vertex at once is to sort them in decreasing index order:
    for v in reversed(sorted(del_list)):
        g.remove_vertex(v)
    Alternatively (and preferably), a list (or iterable) may be passed directly as the vertex parameter, and the above is performed internally (in C++)."
    """
    def remove_spider(self, v: Vertex):
        self.g.remove_vertex(v)

    def add_wire(self, s1: Vertex, s2: Vertex, is_hadamard: bool = False) -> Edge:
        e = self.g.add_edge(s1, s2)
        self.hadamard_prop[e] = is_hadamard

        return e


    def remove_wire(self, w: Edge = None, s1: Vertex = None, s2: Vertex = None):
        if w:
            self.g.remove_edge(w)
        elif s1 is not None and s2 is not None:
            edges = set(filter(lambda e: e.source() == s2 or e.target() == s2, s1.all_edges()))
            for e in edges:
                self.g.remove_edge(e)
        else:
            raise RuntimeError("Invalid parameters")

    def add_boundary(self, type: str, qubit_index: int = None, identifier: str = None) -> Vertex:
        assert type in BOUNDARY_NAME_TO_TYPE
        v = self.g.add_vertex()
        self.vertex_type_prop[v] = VERTEX_BOUNDARY
        self.boundary_type_prop[v] = BOUNDARY_NAME_TO_TYPE[type]
        if qubit_index:
            self.boundary_qubit_indices_prop[v] = qubit_index
        if identifier:
            self.vertex_identifier_prop[v] = identifier

        return v

    def remove_boundary(self, b: Vertex):
        self.g.remove_vertex(b)

    def is_spider(self, v: Vertex) -> bool:
        return self.vertex_type_prop[v] == VERTEX_SPIDER_GREEN or self.vertex_type_prop[v] == VERTEX_SPIDER_RED

    def get_spiders(self) -> List[Vertex]:
        return [v for v in self.g.vertices() if self.is_spider(v)]

    def get_spiders_by_color(self, color: str) -> List[Vertex]:
        assert color in SPIDER_COLORS
        return [s for s in self.get_spiders() if self.get_spider_color(s) == color]

    def is_boundary(self, v: Vertex) -> List[Vertex]:
        return self.vertex_type_prop[v] == VERTEX_BOUNDARY
    def is_input(self, v: Vertex):
        return self.is_boundary(v) and self.boundary_type_prop[v] == INPUT
    def is_output(self, v: Vertex):
        return self.is_boundary(v) and self.boundary_type_prop[v] == OUTPUT

    def get_boundaries(self):
        return [v for v in self.g.vertices() if self.is_boundary(v)]

    def get_inputs(self) -> List[Vertex]:
        return [v for v in self.g.vertices() if self.is_input(v)]

    def get_outputs(self) -> List[Vertex]:
        return [v for v in self.g.vertices() if self.is_output(v)]

    def get_boundary_index(self, b: Vertex) -> int:
        return self.boundary_qubit_indices_prop[b]

    def get_spider_qubit_index(self, s: Vertex) -> int:
        return self.spider_qubit_indices_prop[s]

    def is_wire_hadamard(self, e: Edge) -> bool:
        return self.hadamard_prop[e] == 1

    def set_wire_hadamard(self, e: Edge, is_h: bool):
        self.hadamard_prop[e] = is_h

    def get_spider_color(self, s: Vertex) -> str:
        assert self.vertex_type_prop[s] in VERTEX_TYPE_TO_SPIDER_COLOR, "A non spider (boundary) vertex has no color"
        return VERTEX_TYPE_TO_SPIDER_COLOR[self.vertex_type_prop[s]]

    def set_spider_color(self, s: Vertex, color: str):
        assert color in SPIDER_COLORS
        self.vertex_type_prop[s] = SPIDER_COLOR_TO_VERTEX_TYPE[color]

    def get_spider_phase(self, s: Vertex) -> float:
        return self.phase_prop[s]
    def set_spider_phase(self, s: Vertex, phase: float):
        self.phase_prop[s] = phase

    def get_non_boundary_wires(self):
        return [e for e in self.g.edges() if not self.is_boundary(e.source) and not self.is_boundary(e.target)]

    def get_vertex_from_identifier(self, identifier: str) -> Optional[Vertex]:
        for s in self.g.vertices():
            if self.vertex_identifier_prop[s] == identifier:
                return s
        return None


    def clone(self) -> "Diagram":
        return Diagram(self.g.copy())


    """
    Generate a map indicating for each vertex of the diagram, if it is a spider
    Used for matching to exclude boundaries from subisomorphism
    """
    def generate_is_spider_property(self):
        prop = self.g.new_vertex_property("bool")
        for s in self.g.vertices():
            prop[s] = self.is_spider(s)
        return prop

