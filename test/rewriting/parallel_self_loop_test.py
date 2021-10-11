import unittest

from zxopt.data_structures.diagram import Diagram
from zxopt.simplification import ParallelLoopEdgeRemover
from zxopt.visualization import DiagramRenderer, Window

SHOW_REWRITES = True

class ParallelSelfLoopTest(unittest.TestCase):

    def test_parallel_edge_removal(self):
        diagram = Diagram()
        b_in = diagram.add_boundary("in", 0, "b_in")
        b_out = diagram.add_boundary("out", 0, "b_out")
        s1 = diagram.add_spider(0.0, "green", 0, "s1")
        s2 = diagram.add_spider(0.0, "green", 0, "s2")
        w1 = diagram.add_wire(b_in, s1, False)
        w2 = diagram.add_wire(s1, s2, False)
        w3 = diagram.add_wire(s1, s2, False)
        w4 = diagram.add_wire(s2, b_out, False)

        show(diagram)

        remover = ParallelLoopEdgeRemover(diagram)
        remover.remove_parallel_edges()

        show(diagram)

    def test_parallel_edge_removal_second(self):
        diagram = Diagram()
        b_in = diagram.add_boundary("in", 0, "b_in")
        b_out = diagram.add_boundary("out", 0, "b_out")
        s1 = diagram.add_spider(0.0, "green", 0, "s1")
        s2 = diagram.add_spider(0.0, "green", 0, "s2")
        w1 = diagram.add_wire(b_in, s1, False)
        w2 = diagram.add_wire(s1, s2, True)
        w3 = diagram.add_wire(s1, s2, False)
        w4 = diagram.add_wire(s2, b_out, False)

        show(diagram)

        remover = ParallelLoopEdgeRemover(diagram)
        remover.remove_parallel_edges()

        show(diagram)

    def test_parallel_edge_removal_third(self):
        diagram = Diagram()
        b_in = diagram.add_boundary("in", 0, "b_in")
        b_out = diagram.add_boundary("out", 0, "b_out")
        s1 = diagram.add_spider(0.0, "green", 0, "s1")
        s2 = diagram.add_spider(0.0, "green", 0, "s2")
        w1 = diagram.add_wire(b_in, s1, False)
        w2 = diagram.add_wire(s1, s2, True)
        w3 = diagram.add_wire(s1, s2, True)
        w4 = diagram.add_wire(s2, b_out, False)

        show(diagram)

        remover = ParallelLoopEdgeRemover(diagram)
        remover.remove_parallel_edges()

        show(diagram)
        # TODO fix rendering

    def test_self_loop_removal(self):
        diagram = Diagram()
        b_in = diagram.add_boundary("in", 0, "b_in")
        b_out = diagram.add_boundary("out", 0, "b_out")
        s1 = diagram.add_spider(0.0, "green", 0, "s1")
        w1 = diagram.add_wire(b_in, s1, False)
        w2 = diagram.add_wire(s1, s1, False)
        w4 = diagram.add_wire(s1, b_out, False)

        show(diagram)

        remover = ParallelLoopEdgeRemover(diagram)
        remover.remove_self_loops()

        show(diagram)


def show(diagram: Diagram):
    if SHOW_REWRITES:
        renderer = DiagramRenderer(diagram)
        window = Window(renderer)
        window.main_loop()