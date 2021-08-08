
import math

from zxopt.data_structures.diagram import Diagram
from zxopt.visualization import DiagramRenderer, Window

### Test
# Manually creates and renders a diagram
if __name__ == "__main__":
    diagram = Diagram()
    in1 = diagram.add_boundary("in", 0)
    in2 = diagram.add_boundary("in", 1)
    out1 = diagram.add_boundary("out", 0)
    out2 = diagram.add_boundary("out", 1)

    s1_1 = diagram.add_spider(0.0, "green", 0)
    s1_2 = diagram.add_spider(0.0, "red", 1)
    s2_1 = diagram.add_spider(math.pi, "red", 0)

    diagram.add_wire(in1, s1_1)
    diagram.add_wire(in2, s1_2)
    diagram.add_wire(s1_1, s1_2)
    diagram.add_wire(s1_1, s2_1)
    diagram.add_wire(s2_1, out1)
    diagram.add_wire(s1_2, out2)

    renderer = DiagramRenderer(diagram, disable_alignment=False)

    window = Window(renderer)
    window.main_loop()
