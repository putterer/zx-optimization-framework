from typing import Optional

from graph_tool import Graph, VertexPropertyMap, EdgePropertyMap, Vertex, Edge

from zxopt.data_structures.diagram.diagram import SPIDER_COLORS
from zxopt.rewriting.rewrite_phase_expression import RewriteVariable, RewritePhaseExpression

RULE_ONLY_SPIDER_COLORS = {"black", "white", "grey"} # black / white assignable, grey arbitrary
RULE_SPIDER_COLORS = SPIDER_COLORS.union(RULE_ONLY_SPIDER_COLORS)

CONNECTING_WIRES_NONE = 0
CONNECTING_WIRES_ANY = -1

"""
Represents a rewrite rule specifying the source and target graphs as well as their properties and variable mappings
"""
class RewriteRule:
    structure1: "RewriteStructure"
    structure2: "RewriteStructure"
    variable_mapping: dict[RewriteVariable, RewriteVariable]
    connecting_wires_spider_mapping: dict[Vertex, Vertex]

    def __init__(self, s1: "RewriteStructure", s2: "RewriteStructure", variable_mapping: dict[RewriteVariable, RewriteVariable], connecting_wires_spider_mapping: dict[Vertex, Vertex]):
        self.structure1 = s1
        self.structure2 = s2
        self.variable_mapping = variable_mapping
        self.connecting_wires_spider_mapping = connecting_wires_spider_mapping

    """
    Reset all phase expression variables
    """
    def reset(self):
        self.structure1.reset()
        self.structure2.reset()


"""
Represents the source or target graph and structure of a rewrite rule
"""
class RewriteStructure:
    g: Graph  # spiders, inner wires

    connecting_wires_prop: VertexPropertyMap  # multiplicity of connecting wires by spider
    connecting_wires_hadamard_prop: VertexPropertyMap  # number of connecting wires that contain a hadamard gate
    spider_color_prop: VertexPropertyMap  # green, red, white, black
    spider_phase_prop: VertexPropertyMap  # phase expressions
    hadamard_prop: EdgePropertyMap
    variables: set[RewriteVariable]

    assigned_spider_colors: dict[str, Optional[str]]

    def __init__(self):
        self.g = Graph(directed=False)

        self.connecting_wires_prop = self.g.new_vertex_property("int")
        self.connecting_wires_hadamard_prop = self.g.new_vertex_property("int")
        self.spider_color_prop = self.g.new_vertex_property("string")
        self.spider_phase_prop = self.g.new_vertex_property("object")
        self.hadamard_prop = self.g.new_vertex_property("bool")

        self.variables = set()
        self.reset()  # init self.assigned_spider_colors

    def add_spider(self, color: str, phase: RewritePhaseExpression, connecting_wires_count: int, conencting_wires_hadamard_count: int) -> Vertex:
        assert color in RULE_SPIDER_COLORS, "Invalid spider color"

        s = self.g.add_vertex()
        self.spider_color_prop[s] = color
        self.spider_phase_prop[s] = phase
        self.connecting_wires_prop[s] = connecting_wires_count
        self.connecting_wires_hadamard_prop[s] = conencting_wires_hadamard_count

        for v in phase.variables():
            self.variables.add(v)

        return s

    def remove_spider(self, s: Vertex):
        self.g.remove_vertex(s)
        # variables NOT removed as they may be part of other spiders

    def add_wire(self, s1: Vertex, s2: Vertex, is_hadamard: bool) -> Edge:
        w = self.g.add_edge(s1, s2)
        self.hadamard_prop[w] = is_hadamard
        return w

    def remove_wire(self, w: Edge):
        self.g.remove_edge(w)

    """
    Checks and resolves if the inputted color is assignable to the spider part of this rule
    """
    def spider_matches_color(self, spider: Vertex, color: str):
        rule_spider_color: str = self.spider_color_prop[spider]
        if rule_spider_color in SPIDER_COLORS:
            return rule_spider_color == color
        elif rule_spider_color == "grey":
            return True
        elif rule_spider_color in RULE_ONLY_SPIDER_COLORS:
            if self.assigned_spider_colors[rule_spider_color] is None:
                self.assigned_spider_colors[rule_spider_color] = color
                return True
            else:
                return self.assigned_spider_colors[rule_spider_color] == color
        else:
            raise AssertionError(f"Invalid spider color {color}")

    """
    Checks and resolves if the inputted phase is assignable to the spider part of this rule
    Sets variable values of the rule accordingly
    """
    def spider_matches_phase(self, spider: Vertex, phase: float):
        rule_spider_phase_expr: RewritePhaseExpression = self.spider_phase_prop[spider]

        return rule_spider_phase_expr.matches(phase)

    """
    Reset assigned spider colors and phase expression variables
    """
    def reset(self):
        self.assigned_spider_colors = {"white": None, "black": None}

        for v in self.variables:
            v.reset()