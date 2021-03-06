from typing import Dict, List

from graph_tool import Vertex, Edge

from zxopt.data_structures.diagram import Diagram
from zxopt.data_structures.diagram.diagram import OTHER_SPIDER_COLOR
from zxopt.rewriting import RewriteRule, RewritePhaseExpression
from zxopt.rewriting.matcher import ConnectingNeighbor
from zxopt.rewriting.rewrite_rule import SPIDER_COLOR_WHITE, SPIDER_COLOR_BLACK


class Rewriter:
    diagram: Diagram

    def __init__(self, diagram: Diagram):
        self.diagram = diagram

        self.test_qubit_index = 0

    def rewrite(self, rule: RewriteRule, source_to_diagram_map: Dict[Vertex, Vertex], source_spider_to_connected_diagram_neighbors_map: Dict[Vertex, List[ConnectingNeighbor]]):
        source = rule.source
        target = rule.target

        diagram_source_rule_spiders = [source_to_diagram_map[s] for s in source.g.vertices()]

        # resolve variables from source to target
        for source_variable in rule.variable_mapping:
            target_variable = rule.variable_mapping[source_variable]
            target_variable.resolve(source_variable.evaluate())

        # resolve unknown colors
        if rule.source.assigned_spider_colors[SPIDER_COLOR_WHITE] is None and rule.source.assigned_spider_colors[SPIDER_COLOR_BLACK] is not None:
            rule.source.assigned_spider_colors[SPIDER_COLOR_WHITE] = OTHER_SPIDER_COLOR[rule.source.assigned_spider_colors[SPIDER_COLOR_BLACK]]
        if rule.source.assigned_spider_colors[SPIDER_COLOR_BLACK] is None and rule.source.assigned_spider_colors[SPIDER_COLOR_WHITE] is not None:
            rule.source.assigned_spider_colors[SPIDER_COLOR_BLACK] = OTHER_SPIDER_COLOR[rule.source.assigned_spider_colors[SPIDER_COLOR_WHITE]]


        # spiders are removed later as this would invalidate the vertex descriptors used for identifying connecting neighbors


        # Add new nodes based on target structure
        target_to_diagram_map: Dict[Vertex, Vertex] = {}
        for target_spiders in target.g.vertices():
            # calculate qubit index of new spider based on origin connecting wires source spider
            qubit_index = self.get_qubit_index_for_rewritten_spider(target_spiders, rule, source_to_diagram_map)

            # determine color
            new_color = source.assigned_spider_colors[target.spider_color_prop[target_spiders]]
            if not new_color:
                raise ValueError(f"Color {target.spider_color_prop[target_spiders]} has not been resolved yet, cannot assign")

            # determine phase
            new_phase_expression: RewritePhaseExpression = target.spider_phase_prop[target_spiders]
            new_phase = new_phase_expression.evaluate()

            # create target spider
            new_diagram_spider = self.diagram.add_spider(phase=new_phase, color=new_color, origin_qubit_index=qubit_index)
            target_to_diagram_map[target_spiders] = new_diagram_spider

        # Add inner wires from target structure
        target_wire: Edge
        for target_wire in target.g.edges():
            new_wire_source = target_to_diagram_map[target_wire.source()]
            new_wire_target = target_to_diagram_map[target_wire.target()]
            new_wire_is_hadamard = target.hadamard_prop[target_wire]

            new_diagram_wire = self.diagram.add_wire(new_wire_source, new_wire_target, new_wire_is_hadamard)

        # Connect outer wires
        for source_spider in source_spider_to_connected_diagram_neighbors_map:
            target_spiders = rule.connecting_wires_spider_mapping[source_spider]
            connected_diagram_neighbors = source_spider_to_connected_diagram_neighbors_map[source_spider]

            if target_spiders is not None:
                if type(target_spiders) == list:
                    neighbors_to_be_processed = connected_diagram_neighbors.copy()

                    # distribute equally among possible targets
                    while len(neighbors_to_be_processed) > 0:
                        for target_spider in target_spiders:
                            if len(neighbors_to_be_processed) <= 0:
                                break

                            new_diagram_spider = target_to_diagram_map[target_spider]
                            connected_diagram_neighbor = neighbors_to_be_processed[0]
                            neighbors_to_be_processed.remove(connected_diagram_neighbor)  # only first occurence

                            new_wire_is_hadamard = connected_diagram_neighbor.is_hadamard ^ connected_diagram_neighbor.should_be_flipped
                            self.diagram.add_wire(new_diagram_spider, connected_diagram_neighbor.outer_neighbor, is_hadamard=new_wire_is_hadamard)
                else:
                    new_diagram_spider = target_to_diagram_map[target_spiders]
                    for connected_diagram_neighbor in connected_diagram_neighbors:
                        new_wire_is_hadamard = connected_diagram_neighbor.is_hadamard ^ connected_diagram_neighbor.should_be_flipped
                        self.diagram.add_wire(new_diagram_spider, connected_diagram_neighbor.outer_neighbor, is_hadamard=new_wire_is_hadamard)
            else:
                # Connect outer wires if there are no spiders left in the target (e.g. ZX S2 rule)
                # ONLY DO THIS ONCE PER PAIR, otherwise will yield duplicate wires

                for i1 in range(len(connected_diagram_neighbors)):
                    for i2 in range(i1 + 1, len(connected_diagram_neighbors)):
                        n1 = connected_diagram_neighbors[i1]
                        n2 = connected_diagram_neighbors[i2]
                        new_wire_is_hadamard = n1.is_hadamard ^ n1.should_be_flipped ^ n2.is_hadamard ^ n2.should_be_flipped
                        if n1 != n2:
                            self.diagram.add_wire(n1.outer_neighbor, n2.outer_neighbor, is_hadamard=new_wire_is_hadamard)

        self.diagram.remove_spiders(diagram_source_rule_spiders) # also removes inner as well as connecting, outer wires


    def get_qubit_index_for_rewritten_spider(self, target_spider: Vertex, rule: RewriteRule, source_to_diagram_map: Dict[Vertex, Vertex]) -> int:
        source_spiders = [s for s in rule.connecting_wires_spider_mapping if rule.connecting_wires_spider_mapping[s] == target_spider or (type(rule.connecting_wires_spider_mapping[s]) == list and target_spider in rule.connecting_wires_spider_mapping[s])]

        self.test_qubit_index += 1

        return (self.test_qubit_index) % 2 # TODO: test code
        return self.diagram.get_spider_qubit_index(source_to_diagram_map[source_spiders[0]])
