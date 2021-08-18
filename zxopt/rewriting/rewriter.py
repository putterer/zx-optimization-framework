from graph_tool import Vertex, VertexPropertyMap

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule


class Rewriter:
    diagram: Diagram

    def __init__(self, diagram: Diagram):
        self.diagram = diagram

    def rewrite(self, rule: RewriteRule, source_to_diagram_map: VertexPropertyMap, source_spider_to_connected_diagram_neighbors_map: dict[Vertex, list[Vertex]]):
        source = rule.source
        target = rule.target

        diagram_source_rule_spiders = [source_to_diagram_map[s] for s in source.g.vertices()]

        # remove source part in diagram
        for spider in diagram_source_rule_spiders:
            self.diagram.remove_spider(spider) # also removes inner as well as connecting, outer wires

        target_to_diagram_map: dict[Vertex, Vertex] = {}
        for spider in target.g.vertices():
            new_diagram_vertex = self.diagram.add_spider(origin_qubit_index=) # uses DEFAULT PHASE AND COLOR, SET LATER!
            # TODO: where do I get the qubit index from? no direct relationship between source and target structures. conencting wires mapping? phase mapping?