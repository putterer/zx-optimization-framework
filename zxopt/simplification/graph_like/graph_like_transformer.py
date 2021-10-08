from zxopt.data_structures.diagram import Diagram


class GraphLikeTransformer:


    """
    Apply the transformation algorithm as described in "Graph-theoretic Simplification of Quantum Circuits with the ZX-calculus"
    """
    def transform(self, diagram):
        diagram = diagram.clone()

        # Turn red spiders into green spiders, introducing hadamards
        self.eliminate_red_spiders(diagram)
        self.eliminate_non_hadamard_wires(diagram)



    """
    Replace all red (X) spiders by green (Z) spiders
    Duplicate hadamards are automatically resolved via the toggeling mechanism of the edges' hadamard status
    """
    def eliminate_red_spiders(self, diagram: Diagram) -> int:
        spiders_removed = 0
        for x_spider in diagram.get_spiders_by_color("red"):
            diagram.set_spider_color(x_spider, "green")
            spiders_removed += 1
            for wire in x_spider.all_edges():
                diagram.set_wire_hadamard(wire, not diagram.is_wire_hadamard(wire))
        return spiders_removed


    """
    Eliminates all non hadamard edges by fusing neighboring spiders 
    """
    def eliminate_non_hadamard_wires(self, diagram: Diagram) -> int:
        edges_removed = 0

        while True:
            non_hadamard_wires = [w for w in diagram.get_non_boundary_wires() if not diagram.is_wire_hadamard(w)] # also have to be non boundary
            wire = next(non_hadamard_wires)
            if wire == None:
                break

            edges_removed += 1


        return edges_removed
