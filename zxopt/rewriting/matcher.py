from typing import Generator, Optional

from graph_tool import VertexPropertyMap, Vertex, Edge
from graph_tool.topology import subgraph_isomorphism

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule, RewriteStructure
from zxopt.rewriting.connecting_neighbor import ConnectingNeighbor
from zxopt.rewriting.rewrite_rule import CONNECTING_WIRES_ANY
from zxopt.rewriting.rewriter import Rewriter


class Matcher:
    diagram: Diagram
    rewriter: Rewriter

    def __init__(self, diagram: Diagram):
        self.diagram = diagram
        self.rewriter = Rewriter(diagram)

    """
    Match (and applies if specified) the give rule in one direction if possible
    The rule is reset before and contains the matched phases and colors after matching 
    """
    # TODO: separate different parts into multiple functions
    def match_rule(self, rule: RewriteRule, apply: bool = False) -> Optional[dict[Vertex, Vertex]]:
        source = rule.source
        # search graph for subisomorphisms (generate on the fly, don't calculate all at once)
        isomorphism_generator: Generator[VertexPropertyMap] = subgraph_isomorphism(
            source.g,
            self.diagram.g,
            max_n=0,
            vertex_label=(rule.source.generate_is_spider_property(), self.diagram.generate_is_spider_property()), # True if spider -> exclude boundaries
            edge_label=(rule.source.hadamard_prop, self.diagram.hadamard_prop),  # check hadamard prop
            generator=True
        )

        # check those for additional properties
        checked_cases = 0
        rule_to_diagram_index_map: VertexPropertyMap  # maps rule.source -> diagram
        for rule_to_diagram_index_map in isomorphism_generator:
            rule_to_diagram_map: dict[Vertex, Vertex] = {}
            for s in source.g.vertices():
                rule_to_diagram_map[s] = self.diagram.g.vertex(rule_to_diagram_index_map[s])

            checked_cases += 1  # count for performance analysis

            # reset rule
            rule.reset()

            # check and resolve spider colors
            if not self.__match_colors(source, rule_to_diagram_map):
                continue

            # check and resolve spider phases
            if not self.__match_phases(source, rule_to_diagram_map):
                continue

            # check and collect connecting wires to neighbors outside of rule
            connecting_wires_match, source_spider_to_connected_diagram_neighbors_map = self.__match_connecting_wires(source, rule_to_diagram_map)
            if not connecting_wires_match:
                continue

            # Rewrite
            if apply:
                self.rewriter.rewrite(rule, rule_to_diagram_map, source_spider_to_connected_diagram_neighbors_map)

            return rule_to_diagram_map

        return None

    """
    Checks and resolves all spider colors
    """
    def __match_colors(self, source: RewriteStructure, rule_to_diagram_map: dict[Vertex, Vertex]) -> bool:
        for spider in source.g.vertices():
            if not source.spider_matches_color(spider, self.diagram.get_spider_color(rule_to_diagram_map[spider])):
                return False
        return True

    """
    Checks and resolves all spider phases
    """
    def __match_phases(self, source: RewriteStructure, rule_to_diagram_map: dict[Vertex, Vertex]) -> bool:
        for spider in source.g.vertices():
            if not source.spider_matches_phase(spider, self.diagram.get_spider_phase(rule_to_diagram_map[spider])):
                return False
        return True


    """
    Check the number of connected neigbors that are not part of the rule for each rule spider
    :returns a mapping from each rule spider to all neighboring, non rule vertices
    """
    def __match_connecting_wires(self, source: RewriteStructure, rule_to_diagram_map: dict[Vertex, Vertex]) -> tuple[bool, dict[Vertex, list["ConnectingNeighbor"]]]:
        source_spider_to_connected_diagram_neighbors_map: dict[Vertex, list[ConnectingNeighbor]] = {}

        diagram_rule_inner_spiders = [rule_to_diagram_map[source_spider] for source_spider in source.g.vertices()]  # the inner spiders of the diagram the rule is being applied to

        source_spider: Vertex
        for source_spider_rule in source.g.vertices():
            source_spider_diagram = rule_to_diagram_map[source_spider_rule]
            total_connections = 0
            source_spider_to_connected_diagram_neighbors_map[source_spider_rule] = []

            # for n in source_spider.all_neighbors():
            #     if not n in diagram_rule_inner_spiders: # check if this is an outer connection?
            #         total_connections += 1
            #         source_spider_to_connected_diagram_neighbors_map[source_spider].append(n)

            wire: Edge
            for wire in source_spider_diagram.all_edges():
                neighbor: Optional[Vertex] = None
                if wire.source() != source_spider_diagram:
                    neighbor = wire.source()
                elif wire.target() != source_spider_diagram:
                    neighbor = wire.target()
                else:
                    continue # self loop, ignore

                if not neighbor in diagram_rule_inner_spiders:
                    total_connections += 1
                    source_spider_to_connected_diagram_neighbors_map[source_spider_rule].append(ConnectingNeighbor(wire, neighbor, self.diagram.is_wire_hadamard(wire)))

            if source.connecting_wires_prop[source_spider_rule] != CONNECTING_WIRES_ANY and len(source_spider_to_connected_diagram_neighbors_map[source_spider_rule]) > source.connecting_wires_prop[source_spider_rule]:
                return False, {}

            # Mark wires to be flipped
            for i in range(0, source.connecting_wires_hadamard_prop[source_spider_rule]):
                source_spider_to_connected_diagram_neighbors_map[source_spider_rule][i].should_be_flipped = True

        return True, source_spider_to_connected_diagram_neighbors_map