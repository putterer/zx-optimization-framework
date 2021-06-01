from graph_tool import Graph, VertexPropertyMap, Vertex, Edge

VERTEX_BOUNDARY = "BOUNDARY"
VERTEX_SPIDER_GREEN = "SPIDER_GREEN"
VERTEX_SPIDER_RED = "SPIDER_RED"
SPIDER_COLOR_TO_VERTEX_TYPE = {"green": VERTEX_SPIDER_GREEN, "red": VERTEX_SPIDER_RED}

INPUT = "IN"
OUTPUT = "OUT"
BOUNDARY_NAME_TO_TYPE = {"in": INPUT, "out": OUTPUT, "IN": INPUT, "OUT": OUTPUT}

class Diagram:
    g: Graph
    vertex_type_prop: VertexPropertyMap
    phase_prop: VertexPropertyMap
    boundary_type_prop: VertexPropertyMap

    def __init__(self, g: Graph = None):
        g = (g if g is not None else Graph(directed=False)) # what the heck python, default constructor parameters are only evaluated once
        self.g = g

        if not "vertex_type_prop" in self.g.vertex_properties:
            self.vertex_type_prop = g.new_vertex_property("string")
            self.phase_prop = g.new_vertex_property("float")
            self.hadamard_prop = g.new_edge_property("bool")
            self.boundary_type_prop = g.new_vertex_property("string")

            self.g.vertex_properties["vertex_type_prop"] = self.vertex_type_prop # internal property map, is included in copy() for cloning
            self.g.vertex_properties["phase_prop"] = self.phase_prop
            self.g.edge_properties["hadamard_prop"] = self.hadamard_prop
            self.g.vertex_properties["boundary_type_prop"] = self.boundary_type_prop
        else:
            self.vertex_type_prop = self.g.vertex_properties["vertex_type_prop"]
            self.phase_prop = self.g.vertex_properties["phase_prop"]
            self.hadamard_prop = self.g.edge_properties["hadamard_prop"]
            self.boundary_type_prop = self.g.vertex_properties["boundary_type_prop"]


    def add_spider(self, phase: float = 0.0, color: str = "green") -> Vertex:
        v = self.g.add_vertex()
        self.vertex_type_prop[v] = SPIDER_COLOR_TO_VERTEX_TYPE[color]
        self.phase_prop[v] = phase

        return v

    def remove_spider(self, v: Vertex):
        self.g.remove_vertex(v)

        # TODO: delete from property map, is this done automatically? the data structure is managed by native code
        # del self.vertex_type_prop[v]
        # del self.phase_prop[v]

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

    def add_boundary(self, type: str) -> Vertex:
        assert type in BOUNDARY_NAME_TO_TYPE
        v = self.g.add_vertex()
        self.vertex_type_prop[v] = VERTEX_BOUNDARY
        self.boundary_type_prop[v] = BOUNDARY_NAME_TO_TYPE[type]

        return v

    def remove_boundary(self, b: Vertex):
        self.g.remove_vertex(b)

    def clone(self) -> "Diagram":
        return Diagram(self.g.copy())

