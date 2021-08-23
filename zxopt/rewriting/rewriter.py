from graph_tool import Vertex, VertexPropertyMap, Edge

from zxopt.data_structures.diagram import Diagram
from zxopt.rewriting import RewriteRule, RewritePhaseExpression


class Rewriter:
    diagram: Diagram

    def __init__(self, diagram: Diagram):
        self.diagram = diagram

    def rewrite(self, rule: RewriteRule, source_to_diagram_map: VertexPropertyMap, source_spider_to_connected_diagram_neighbors_map: dict[Vertex, list[Vertex]]):
        source = rule.source
        target = rule.target

        diagram_source_rule_spiders = [source_to_diagram_map[s] for s in source.g.vertices()]

        # resolve variables from source to target
        for source_variable in rule.variable_mapping:
            target_variable = rule.variable_mapping[source_variable]
            target_variable.resolve(source_variable.evaluate())

        # remove source part in diagram
        for spider in diagram_source_rule_spiders:
            self.diagram.remove_spider(spider) # also removes inner as well as connecting, outer wires


        # Add new nodes based on target structure
        target_to_diagram_map: dict[Vertex, Vertex] = {}
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
            new_diagram_spider = self.diagram.add_spider(phase=new_phase, color=new_color, origin_qubit_index=qubit_index) # TODO uses DEFAULT PHASE AND COLOR, SET LATER!
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
            new_diagram_spider = target_to_diagram_map[target_spider]
            for connected_diagram_neighbor in source_spider_to_connected_diagram_neighbors_map[source_spider]:
                flip_hadamard = "Who knows?" == True # TODO: based on count, how to select / how many, HOW TO KNOW?
                old_wire_is_hadamard = "Who knows?" == True
                new_wire_is_hadamard = old_wire_is_hadamard ^ flip_hadamard

                self.diagram.add_wire(new_diagram_spider, connected_diagram_neighbor, is_hadamard=new_wire_is_hadamard)

                # TODO: connecting wires hadamard prop, would require knowing if the wire had a hadmard before,
                #  but __match_connecting_wires uses all_neighbors, therefore doesn't see all wires and their associated hadamard prop


    def get_qubit_index_for_rewritten_spider(self, target_spider: Vertex, rule: RewriteRule, source_to_diagram_map: VertexPropertyMap) -> int:
        source_spiders = [s for s in rule.connecting_wires_spider_mapping if rule.connecting_wires_spider_mapping[s] == target_spider]

        return self.diagram.get_spider_qubit_index(source_to_diagram_map[source_spiders[0]])
