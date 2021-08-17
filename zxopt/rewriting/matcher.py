from typing import Generator

from graph_tool import VertexPropertyMap, Vertex
from graph_tool.topology import subgraph_isomorphism

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule, RewriteStructure


class Matcher:
    diagram: Diagram

    def __init__(self, diagram: Diagram):
        self.diagram = diagram

    """
    Match (and applies if specified) the give rule in one direction if possible
    """
    # TODO: separate different parts into multiple functions
    def match_rule(self, rule: RewriteRule, apply: bool = False):
        source = rule.structure1
        # search graph for subisomorphisms (generate on the fly, don't calculate all at once)
        isomorphism_generator: Generator[VertexPropertyMap] = subgraph_isomorphism(
            source.g,
            self.diagram.g,
            max_n=0,
            edge_label=(rule.structure1.hadamard_prop, self.diagram.hadamard_prop),  # check hadamard prop
            generator=True
        )

        # check those for additional properties
        checkedCases = 0
        rule_to_diagram_map: VertexPropertyMap  # maps rule.source -> diagram
        for rule_to_diagram_map in isomorphism_generator:
            checkedCases += 1  # count for performance analysis

            # reset rule
            rule.reset()

            # check and resolve spider colors
            if not self.__match_colors(source, rule_to_diagram_map):
                continue

            # check and resolve spider phases
            if not self.__match_phases(source, rule_to_diagram_map):
                continue


            connecting_wires_match, source_spider_to_connected_diagram_neighbors_map = self.__match_connecting_wires(source, rule_to_diagram_map)
            if not connecting_wires_match:
                continue

            # TODO next: rewrite

    """
    Checks and resolves all spider colors
    """
    def __match_colors(self, source: RewriteStructure, rule_to_diagram_map: VertexPropertyMap) -> bool:
        for spider in source.g.vertices():
            if not source.spider_matches_color(spider, self.diagram.get_spider_color(rule_to_diagram_map[spider])):
                return False
        return True

    """
    Checks and resolves all spider phases
    """
    def __match_phases(self, source: RewriteStructure, rule_to_diagram_map: VertexPropertyMap) -> bool:
        for spider in source.g.vertices():
            if not source.spider_matches_phase(spider, self.diagram.get_spider_phase(rule_to_diagram_map[spider])):
                return False
        return True


    """
    Check the number of connected neigbors that are not part of the rule for each rule spider
    :returns a mapping from each rule spider to all neighboring, non rule vertices
    """
    def __match_connecting_wires(self, source: RewriteStructure, rule_to_diagram_map: VertexPropertyMap) -> tuple[bool, dict[Vertex, list[Vertex]]]:
        source_spider_to_connected_diagram_neighbors_map: dict[Vertex, list[Vertex]] = {}

        diagram_rule_inner_spiders = [rule_to_diagram_map[source_spider] for source_spider in source.g.vertices()]  # the inner spiders of the diagram the rule is being applied to

        source_spider: Vertex
        for source_spider in source.g.vertices():
            total_connections = 0
            source_spider_to_connected_diagram_neighbors_map[source_spider] = []

            for n in source_spider.all_neighbors():
                if not n in diagram_rule_inner_spiders: # check if this is an outer connection?   # TODO: does this work? IT DOES NOT WORK, THIS SEARCHES KEY SPACE!
                    total_connections += 1
                    source_spider_to_connected_diagram_neighbors_map[source_spider].append(n)


            if len(source_spider_to_connected_diagram_neighbors_map[source_spider]) > source.connecting_wires_prop[source_spider]:
                return False, {}

        return True, source_spider_to_connected_diagram_neighbors_map


