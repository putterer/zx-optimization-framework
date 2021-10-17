from typing import Optional, Dict, Set, List, Union

from graph_tool import Graph, VertexPropertyMap, EdgePropertyMap, Vertex, Edge

from zxopt.data_structures.diagram.diagram import SPIDER_COLORS
from zxopt.rewriting.rewrite_phase_expression import RewriteVariable, RewritePhaseExpression

SPIDER_COLOR_WHITE = "white"
SPIDER_COLOR_BLACK = "black"
RULE_ONLY_SPIDER_COLORS = {SPIDER_COLOR_BLACK, SPIDER_COLOR_WHITE, "grey"} # black / white assignable, grey arbitrary
OTHER_RULE_ONLY_SPIDER_COLOR = {SPIDER_COLOR_BLACK: SPIDER_COLOR_WHITE, SPIDER_COLOR_WHITE: SPIDER_COLOR_BLACK}
RULE_SPIDER_COLORS = SPIDER_COLORS.union(RULE_ONLY_SPIDER_COLORS)

CONNECTING_WIRES_NONE = 0
CONNECTING_WIRES_ANY = -1

"""
Represents a rewrite rule specifying the source and target graphs as well as their properties and variable mappings
"""
class RewriteRule:
    source: "RewriteStructure"
    target: "RewriteStructure"
    variable_mapping: Dict[RewriteVariable, RewriteVariable]
    connecting_wires_spider_mapping: Dict[Vertex, Union[Vertex, List[Vertex], None]]  # a mapping from spiders of the source to the target used for transferring external, connecting wires
    name: str

    inverse_rule: Optional["RewriteRule"] # this rule's inverse, generated on demand, recursive reference

    def __init__(self,
                 s1: "RewriteStructure" = None, # welcome to python, only evaluated once
                 s2: "RewriteStructure" = None,
                 variable_mapping: Dict[RewriteVariable, RewriteVariable] = None,
                 connecting_wires_spider_mapping: Dict[Vertex, Vertex] = None,
                 name: str = None):
        self.source = s1 if s1 is not None else RewriteStructure()
        self.target = s2 if s2 is not None else RewriteStructure()
        self.variable_mapping = variable_mapping if variable_mapping is not None else {}
        self.connecting_wires_spider_mapping = connecting_wires_spider_mapping if connecting_wires_spider_mapping is not None else {}

        self.inverse_rule = None

        if name is not None:
            self.name = name
        else:
            self.name = str(type(self))

    """
    Reset all phase expression variables
    """
    def reset(self):
        self.source.reset()
        self.target.reset()

    """
    Return this rule's inverse, THEY SHARE REWRITE VARIABLES AND COLORS IN COMMON!
    """
    def inverse(self):
        if self.inverse_rule is None:
            self.__generate_inverse()
        return self.inverse_rule

    def __generate_inverse(self):
        # inversed_connecting_wires_mapping = {self.connecting_wires_spider_mapping[s]: s for s in self.connecting_wires_spider_mapping}
        inversed_connecting_wires_mapping = {}

        for target_vertex in self.target.g.vertices():
            spiders_pointing_to_vertex = [s for s in self.connecting_wires_spider_mapping if self.connecting_wires_spider_mapping[s] == target_vertex or (type(self.connecting_wires_spider_mapping[s]) == list and target_vertex in self.connecting_wires_spider_mapping[s])]
            if len(spiders_pointing_to_vertex) == 0:
                inversed_connecting_wires_mapping[target_vertex] = None
            elif len(spiders_pointing_to_vertex) == 1:
                inversed_connecting_wires_mapping[target_vertex] = spiders_pointing_to_vertex[0]
            else:
                inversed_connecting_wires_mapping[target_vertex] = spiders_pointing_to_vertex


        self.inverse_rule = RewriteRule(
            self.target,
            self.source,
            {self.variable_mapping[s]: s for s in self.variable_mapping},
            inversed_connecting_wires_mapping,
            name=f"{self.name} INVERSE"
        )



"""
Represents the source or target graph and structure of a rewrite rule
"""
class RewriteStructure:
    g: Graph  # spiders, inner wires

    connecting_wires_prop: VertexPropertyMap  # multiplicity of connecting wires by spider
    connecting_wires_hadamard_prop: VertexPropertyMap  # number of connecting wires that contain a hadamard gate, NOT USED FOR MATCHING, JUST FOR FLIPPING
    spider_color_prop: VertexPropertyMap  # green, red, white, black
    spider_phase_prop: VertexPropertyMap  # phase expressions
    hadamard_prop: EdgePropertyMap
    variables: Set[RewriteVariable]

    assigned_spider_colors: Dict[str, Optional[str]]

    def __init__(self):
        self.g = Graph(directed=False)

        self.connecting_wires_prop = self.g.new_vertex_property("int")
        self.connecting_wires_hadamard_prop = self.g.new_vertex_property("int")
        self.spider_color_prop = self.g.new_vertex_property("string")
        self.spider_phase_prop = self.g.new_vertex_property("object")
        self.hadamard_prop = self.g.new_edge_property("bool")

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
        if rule_spider_color in SPIDER_COLORS: # green, red
            return rule_spider_color == color
        elif rule_spider_color == "grey":
            return True
        elif rule_spider_color in RULE_ONLY_SPIDER_COLORS:
            if OTHER_RULE_ONLY_SPIDER_COLOR[rule_spider_color] is not None and self.assigned_spider_colors[OTHER_RULE_ONLY_SPIDER_COLOR[rule_spider_color]] == color: # grey and white need to be different color
                return False

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
        self.assigned_spider_colors = {"white": None, "black": None, "green": "green", "red": "red"}

        for v in self.variables:
            v.reset()


    """
    Generate a map indicating for each vertex of the diagram, if it is a spider (True for all) 
    """
    def generate_is_spider_property(self):
        prop = self.g.new_vertex_property("bool")
        for s in self.g.vertices():
            prop[s] = True
        return prop