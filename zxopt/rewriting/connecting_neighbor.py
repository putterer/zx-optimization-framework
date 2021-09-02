from graph_tool import Edge, Vertex


class ConnectingNeighbor:
    wire: Edge
    outer_neighbor: Vertex
    is_hadamard: bool
    should_be_flipped: bool

    def __init__(self, wire: Edge, outer_neighbor: Vertex, is_hadamard: bool, should_be_flipped: bool = False):  # should be flipped may be set later
        self.wire = wire
        self.outer_neighbor = outer_neighbor
        self.is_hadamard = is_hadamard
        self.should_be_flipped = should_be_flipped