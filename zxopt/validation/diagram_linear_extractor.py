import numpy as np

from zxopt.data_structures.diagram import Diagram
from zxopt.util import Loggable


class DiagramLinearExtractor(Loggable):
    diagram: Diagram
    qubit_count: int

    def __init__(self, diagram: Diagram):
        super(DiagramLinearExtractor, self).__init__()
        self.diagram = diagram
        self.qubit_count = len(diagram.get_inputs())

    def extract_matrix(self):
        # replace X by Z nodes (easier to calculate tensors for)
        diagram = Diagram(self.diagram.g) # TODO: THIS DOES NOT CLONE
        for x_spider in diagram.get_spiders_by_color("red"):
            diagram.set_spider_color(x_spider, "green")
            for wire in x_spider.all_edges():
                diagram.set_wire_hadamard(wire, not diagram.is_wire_hadamard(wire))


        graph =

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

    def generate_tensor(self):
        # how to align
        pass