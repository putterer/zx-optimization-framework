import numpy as np
import tensornetwork
from graph_tool import Edge, Vertex

from zxopt.data_structures.circuit import HadamardGateType
from zxopt.data_structures.diagram import Diagram
from zxopt.simplification.graph_like import GraphLikeTransformer
from zxopt.util import Loggable

HADAMARD_TENSOR = HadamardGateType().matrix

class DiagramLinearExtractor(Loggable):
    diagram: Diagram
    qubit_count: int

    def __init__(self, diagram: Diagram):
        super(DiagramLinearExtractor, self).__init__()
        self.diagram = diagram
        self.qubit_count = len(diagram.get_inputs())

    def extract_matrix(self):
        # replace X by Z nodes (easier to calculate tensors for)
        diagram = self.diagram.clone()
        GraphLikeTransformer().eliminate_red_spiders(diagram)

        # replace hadamard wires by nodes
        graph = diagram.g
        hadamard_wires: list[Edge] = [w for w in graph.edges() if diagram.is_wire_hadamard(w)]
        hadamard_nodes = []
        for wire in hadamard_wires:
            node = graph.add_vertex(1)
            hadamard_nodes.append(node)
            graph.add_edge(wire.source(), node)
            graph.add_edge(node, wire.target())

            graph.remove_edge(wire)

        # Calculate node tensors
        tensor_property = graph.new_vertex_property("object")

        node: Vertex
        for node in graph.vertices():
            if node in hadamard_nodes:
                tensor_property[node] = HADAMARD_TENSOR
                continue
            if diagram.is_spider(node): # exclude inputs/outputs
                assert diagram.get_spider_color(node) == "green"
                # assumes no duplicate wires
                legs = len(list(node.all_neighbors()))
                tensor_property[node] = self.generate_z_tensor(legs, diagram.get_spider_phase(node))


        # Determine wire indices
        wire_index_property = graph.new_edge_property("int")
        indexed_wires = 0

        wire: Edge
        for wire in graph.edges():
            if not diagram.is_boundary(wire.source()) and not diagram.is_boundary(wire.target()):
                wire_index_property[wire] = indexed_wires + 1
                indexed_wires += 1

        inputs = diagram.get_inputs()
        outputs = diagram.get_outputs()
        inputs.sort(key=lambda b: diagram.get_boundary_index(b))
        outputs.sort(key=lambda b: diagram.get_boundary_index(b))

        # Boundary wire indices
        current_boundary_index = -1
        for i in range(len(outputs)):
            wire_index_property[next(outputs[i].all_edges())] = current_boundary_index
            current_boundary_index -= 1
        for i in range(len(inputs)):
            wire_index_property[next(inputs[i].all_edges())] = current_boundary_index
            current_boundary_index -= 1

        # prepare ncon call
        tensor_nodes = [n for n in graph.vertices() if not diagram.is_boundary(n)]
        tensors = [tensor_property[n] for n in tensor_nodes]
        wires_by_tensor = [tuple([wire_index_property[wire] for wire in n.all_edges()]) for n in tensor_nodes]

        # contract tensor network
        contraction = tensornetwork.ncon(tensors, wires_by_tensor)
        result = contraction.reshape((2**len(outputs), 2**len(inputs)))

        return result

    def generate_z_tensor(self, legs: int, phase: float) -> np.ndarray:
        assert legs < 15, f"I am not going to allocate a {legs}-dimensional tensor..."
        tensor = np.zeros(2 ** legs, dtype=np.complex)
        tensor[0] = 1
        tensor[2 ** legs - 1] = np.exp(1j * phase)
        tensor = tensor.reshape((2,) * legs)
        return tensor