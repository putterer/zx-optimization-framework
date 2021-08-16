from typing import Generator

from graph_tool import VertexPropertyMap
from graph_tool.topology import subgraph_isomorphism

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule


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
        rule_to_diagram_map: VertexPropertyMap  # maps rule.source -> diagram
        for rule_to_diagram_map in isomorphism_generator:
            # check and resolve spider colors
            for s in source.g.vertices():
                if not source.spider_matches_color(s, self.diagram.get_spider_color(rule_to_diagram_map[s])):
                    continue

            # check and resolve spider colors
            for s in source.g.vertices():
                if not source.spider_matches_phase(s, self.diagram.get_spider_phase(rule_to_diagram_map[s])):
                    continue

            # TODO next: check connecting wire constraints






    # TODO: separate
    """
    Checks additional properties of the diagram / rule of a subgraph isomorphism
    Resolves phase expression variables and spider colors
    """
    def match_subiso_additional_properties(self) -> bool:
        pass

    def __match_colors(self) -> bool:
        pass