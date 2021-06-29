import numpy as np
from graph_tool import Edge, Vertex

from zxopt.data_structures.circuit import HadamardGateType
from zxopt.data_structures.diagram import Diagram
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
        # TODO: test step by step
        # replace X by Z nodes (easier to calculate tensors for)
        diagram = self.diagram.clone()
        for x_spider in diagram.get_spiders_by_color("red"):
            diagram.set_spider_color(x_spider, "green")
            for wire in x_spider.all_edges():
                diagram.set_wire_hadamard(wire, not diagram.is_wire_hadamard(wire))

        # replace hadamard wires by nodes
        graph = diagram.g
        hadamard_wires: list[Edge] = [w for w in graph.edges() if diagram.is_wire_hadamard()]
        hadamard_nodes = []
        for wire in hadamard_wires:
            graph.remove_edge(wire)

            node = graph.add_vertex(1)
            hadamard_nodes.append(node)
            graph.add_edge(wire.source(), node)
            graph.add_edge(node, wire.target())

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
                legs = node.all_neighbors()
                tensor_property[node] = self.generate_z_tensor(legs, diagram.get_spider_phase(node))


        # Determine wire indices
        edge_index_property = graph.new_edge_property("int")
        indexed_wires = 0

        wire: Edge
        for wire in graph.edges():
            if not diagram.is_boundary(wire.source()) and not diagram.is_boundary(wire.target()):
                edge_index_property[wire] = indexed_wires
                indexed_wires += 1

        inputs = diagram.get_inputs()
        outputs = diagram.get_outputs()
        inputs.sort(key=lambda b: diagram.get_boundary_index(b))
        outputs.sort(key=lambda b: diagram.get_boundary_index(b))

        for i in range(len(inputs)): # TODO: how to order indices?
            pass
        for i in range(len(inputs)): # TODO: how to order indices?
            pass

        # TODO: call ncon with tensors and tuples of adjacent edge indices for each

        # tensor network
        #
        # → replace X by Z nodes
        # represent spiders as tensors (one dimension per leg, dimension size = 2)
        # represent hadamard as nodes
        # label edges, negative labels for dangling
        # generate tensors
        #  --> what are inputs, what are outputs???? can probably arbitrarily align (flow through network?)
        # contract
        # np.einsum or https://tensornetwork.readthedocs.io/en/latest/ncon.html for contraction



        return np.identity(2 ** self.qubit_count) # TODO: return actual matrix

    def generate_z_tensor(self, legs: int, phase: float) -> np.ndarray:
        assert legs < 15, f"I am not going to allocate a {legs}-dimensional tensor..."
        tensor = np.zeros(2 ** legs, dtype=np.complex)
        tensor[0] = 1
        tensor[2 ** legs - 1] = np.exp(1j * phase)
        tensor = tensor.reshape((2,) * legs)
        return tensor