

"""
Represents a rewrite rule specifying the source and target graphs as well as their properties and variable mappings
"""
from typing import Optional

from graph_tool import Graph, VertexPropertyMap, EdgePropertyMap

from zxopt.rewriting.RewritePhaseExpression import RewriteVariable


class RewriteRule:
    structure1: "RewriteStructure"
    structure2: "RewriteStructure"
    variable_mapping: list[tuple[RewriteVariable, RewriteVariable]]

    def __init__(self):
        pass


# Connecting wire multiplicities
ARBITRARY_MULTIPLICITY = -1
NO_CONNECTING_WIRES = 0

"""
Represents the source or target graph and structure of a rewrite rule
"""
class RewriteStructure:
    g: Graph  # spiders, inner wires

    connecting_wires_prop: VertexPropertyMap  # multiplicity of connecting wires by spider
    spider_color_prop: VertexPropertyMap  # green, red, white, black
    spider_phase_prop: VertexPropertyMap  # phase expressions
    hadamard_prop: EdgePropertyMap
    variables: list[RewriteVariable]

    assigned_white_spider_color: Optional[str]
    assigned_black_spider_color: Optional[str]

    def __init__(self):
        self.g = Graph(directed=False)

        self.connecting_wires_prop = self.g.new_vertex_property("int")
        self.spider_color_prop = self.g.new_vertex_property("string")
        self.spider_phase_prop = self.g.new_vertex_property("object")
        self.hadamard_prop = self.g.new_vertex_property("bool")

        self.variables = []
        self.assigned_white_spider_color = None
        self.assigned_black_spider_color = None

    def add_spider(self):
        pass # Todo: also set properties correctly (from parameters)

    def remove_spider(self):
        pass

    def add_wire(self):
        pass

    def remove_wire(self):
        pass

    """
    Reset assigned spider colors and phase expression variables
    """
    def reset(self):
        self.assigned_white_spider_color = None
        self.assigned_black_spider_color = None
        for v in self.variables:
            v.reset()