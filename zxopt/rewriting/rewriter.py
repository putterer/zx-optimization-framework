from typing import Dict, List

from graph_tool import Vertex, Edge

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule, RewritePhaseExpression
from zxopt.rewriting.matcher import ConnectingNeighbor


class Rewriter:
    diagram: Diagram

    def __init__(self, diagram: Diagram):
        self.diagram = diagram

    def rewrite(self, rule: RewriteRule, source_to_diagram_map: Dict[Vertex, Vertex], source_spider_to_connected_diagram_neighbors_map: Dict[Vertex, List[ConnectingNeighbor]]):
        source = rule.source
        target = rule.target

        diagram_source_rule_spiders = [source_to_diagram_map[s] for s in source.g.vertices()]

        # resolve variables from source to target
        for source_variable in rule.variable_mapping:
            target_variable = rule.variable_mapping[source_variable]
            target_variable.resolve(source_variable.evaluate())


        # spiders are removed later as this would invalidate the vertex descriptors used for identifying connecting neighbors


        # Add new nodes based on target structure
        target_to_diagram_map: Dict[Vertex, Vertex] = {}
        for target_spider in target.g.vertices():
            # calculate qubit index of new spider based on origin connecting wires source spider
            qubit_index = self.get_qubit_index_for_rewritten_spider(target_spider, rule, source_to_diagram_map)

            # determine color
            new_color = source.assigned_spider_colors[target.spider_color_prop[target_spider]]
            if not new_color:
                raise ValueError(f"Color {target.spider_color_prop[target_spider]} has not been resolved yet, cannot assign")

            # determine phase
            new_phase_expression: RewritePhaseExpression = target.spider_phase_prop[target_spider]
            new_phase = new_phase_expression.evaluate()

            # create target spider
            new_diagram_spider = self.diagram.add_spider(phase=new_phase, color=new_color, origin_qubit_index=qubit_index)
            target_to_diagram_map[target_spider] = new_diagram_spider

        # Add inner wires from target structure
        target_wire: Edge
        for target_wire in target.g.edges():
            new_wire_source = target_to_diagram_map[target_wire.source()]
            new_wire_target = target_to_diagram_map[target_wire.target()]
            new_wire_is_hadamard = target.hadamard_prop[target_wire]

            new_diagram_wire = self.diagram.add_wire(new_wire_source, new_wire_target, new_wire_is_hadamard)

        # Connect outer wires
        for source_spider in source_spider_to_connected_diagram_neighbors_map:
            target_spider = rule.connecting_wires_spider_mapping[source_spider]
            connected_diagram_neighbors = source_spider_to_connected_diagram_neighbors_map[source_spider]

            if target_spider is not None:
                new_diagram_spider = target_to_diagram_map[target_spider]
                for connected_diagram_neighbor in connected_diagram_neighbors:
                    new_wire_is_hadamard = connected_diagram_neighbor.is_hadamard ^ connected_diagram_neighbor.should_be_flipped
                    self.diagram.add_wire(new_diagram_spider, connected_diagram_neighbor.outer_neighbor, is_hadamard=new_wire_is_hadamard)
            else:
                # Connect outer wires if there are no spiders left in the target (e.g. ZX S2 rule)
                for n1 in connected_diagram_neighbors:
                    for n2 in connected_diagram_neighbors:
                        new_wire_is_hadamard = n1.is_hadamard ^ n1.should_be_flipped ^ n2.is_hadamard ^ n2.should_be_flipped
                        if n1 != n2:
                            self.diagram.add_wire(n1.outer_neighbor, n2.outer_neighbor, is_hadamard=new_wire_is_hadamard)

        self.diagram.remove_spiders(diagram_source_rule_spiders) # also removes inner as well as connecting, outer wires


    def get_qubit_index_for_rewritten_spider(self, target_spider: Vertex, rule: RewriteRule, source_to_diagram_map: Dict[Vertex, Vertex]) -> int:
        source_spiders = [s for s in rule.connecting_wires_spider_mapping if rule.connecting_wires_spider_mapping[s] == target_spider]

        return self.diagram.get_spider_qubit_index(source_to_diagram_map[source_spiders[0]])
